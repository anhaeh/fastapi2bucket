# encoding: utf-8
import unittest
from datetime import datetime
from unittest import mock
from dateutil.tz import tzutc
from .base import BaseTest
from modules.s3_client import S3Client


class TestS3Client(BaseTest):

    @mock.patch("boto3.client")
    def test_get_list_empty(self, mock_client):
        mock_client.return_value = mock_client
        mock_client.list_objects.return_value = {}
        client = S3Client()
        result = client.get_list('test')
        self.assertEqual(result, [])

    @mock.patch("boto3.client")
    def test_get_list(self, mock_client):
        mock_client.return_value = mock_client
        mock_client.list_objects.return_value = {
            "Contents": [
                {
                    'Key': 'test.jpg',
                    'LastModified': datetime(2021, 1, 12, 20, 1, 50, tzinfo=tzutc()),
                    'ETag': '"f9c6049f17006504d1981a16385980d8"', 'Size': 369155, 'StorageClass': 'STANDARD',
                    'Owner': {
                        'DisplayName': 'cto',
                        'ID': '59604054b3e736e42d902be7c00d15dc1f6360eb93c900ca17eaa2b5890bcaf2'
                    }
                }
            ]
        }

        client = S3Client()
        result = client.get_list('', True)
        expected_result = [
            {
                'modified': '2021-01-12T20:01:50+00:00',
                'name': 'test.jpg',
                'size': 369155,
                'url': 'https://test-bucket/test.jpg'
             }
        ]
        self.assertEqual(result, expected_result)

    @mock.patch("boto3.client")
    def test_upload(self, mock_client):
        mock_client.return_value = mock_client
        mock_client.upload_fileobj.return_value = {"result": 1}
        client = S3Client()
        url = client.upload('sample.png', {}, 'image')
        expected_url = "https://test-bucket/sample.png"
        self.assertEqual(expected_url, url)

    @mock.patch("boto3.client")
    def test_delete(self, mock_client):
        mock_client.return_value = mock_client
        mock_client.delete_objects.return_value = {
            "Deleted": [
                {
                    "Key": "dev/logo-tools/xx/tunnel_16105643036960301.jpg"
                }
            ],
            "ResponseMetadata": {}
        }
        client = S3Client()
        response = client.delete('sample.png')
        self.assertIs(type(response), dict)


if __name__ == '__main__':
    unittest.main()
