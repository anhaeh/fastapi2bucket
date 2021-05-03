# encoding: utf-8
import boto3
import json

from os import path
from modules.settings import get_setting
from modules.cache import get_cache_client
from fastapi import HTTPException
from typing import BinaryIO


class S3Exception(HTTPException):
    def __init__(self, message):
        super(S3Exception, self).__init__(detail=message, status_code=400)


class S3Client:

    def __init__(self):
        self.cache = get_cache_client()
        self.config = get_setting()

    def _get_client(self):
        try:
            client = boto3.client('s3',
                                  aws_access_key_id=self.config.aws_access_key_id,
                                  aws_secret_access_key=self.config.aws_secret_access_key,
                                  region_name=self.config.region
                                  )
        except Exception as e:
            raise S3Exception(repr(e))
        return client

    def _get_file_url(self, url: str):
        """
        :rtype: str
        """
        host = self.config.bucket_name if not self.config.aws_host else f'{self.config.bucket_name}.{self.config.aws_host}'
        return f"https://{host}/{url}"

    def _normalized_content(self, item: dict):
        return {
            'name': item['Key'].split('/')[-1],
            'url': self._get_file_url(item['Key']),
            'modified': item['LastModified'].isoformat(),
            'size': item['Size']
        }

    def get_list(self, prefix: str = '', skip_cache: bool = False):
        """
        :return: images list
        :rtype: list
        """
        response = None if skip_cache else self.cache.get(prefix)
        if not response:
            client = self._get_client()
            try:
                response = client.list_objects(
                    Bucket=self.config.bucket_name,
                    Prefix=prefix
                )
                content = response.get("Contents", [])
                content.sort(key=lambda x: x['LastModified'], reverse=True)
                content = list(map(self._normalized_content, content))
                response = json.dumps(content)
                self.cache.set(prefix, response)
            except Exception as e:
                raise S3Exception(repr(e))
        return json.loads(response)

    def upload(self, url: str, file: BinaryIO, content_type: str):
        """
        :return: image url
        :rtype: str
        """
        client = self._get_client()
        try:
            client.upload_fileobj(file, self.config.bucket_name, url, ExtraArgs={
                'ACL': 'public-read',
                'ContentType': content_type
            })
            self._delete_list_cache(url)
        except Exception as e:
            raise S3Exception(repr(e))

        return self._get_file_url(url)

    def delete(self, url: str):
        """
        :return: result s3 details
        :rtype: dict
        """
        result = None
        client = self._get_client()
        try:
            result = client.delete_objects(
                Bucket=self.config.bucket_name,
                Delete={
                    'Objects': [{
                        'Key': url
                    }]
                }
            )
            self._delete_list_cache(url)
        except Exception as e:
            print("error in delete file", str(e))
        return result

    def _delete_list_cache(self, url):
        pattern = path.dirname(url)
        return self.cache.delete_by_pattern(pattern)
