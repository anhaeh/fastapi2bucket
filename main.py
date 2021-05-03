# encoding: utf-8
import magic
from base64 import b64decode
from io import BytesIO
from os import path
from pydantic.main import BaseModel
from fastapi import FastAPI, HTTPException, status, Query
from modules.settings import get_setting
from typing import Optional
from modules.s3_client import S3Client


class ImageException(HTTPException):
    def __init__(self, exception):
        super(ImageException, self).__init__(detail=exception, status_code=400)


class Image(BaseModel):
    base64_content: str
    filename: str


app = FastAPI()
c = S3Client()


@app.get("/status/")
def service_status():
    r = {'status': 'ok', 'bucket_name': get_setting().bucket_name, 'errors': []}
    try:
        files = c.get_list('', skip_cache=True)
        r['files_in_env'] = len(files)
    except Exception as e:
        r['status'] = 'error'
        r['errors'].append(f'S3Client:{repr(e)}')
    return r


@app.get("/items/")
def get_files(prefix: Optional[str] = Query('', title="S3 bucket prefix")):
    return c.get_list(prefix)


@app.post("/items/", status_code=status.HTTP_201_CREATED)
def upload_file(image: Image, prefix: Optional[str] = Query('', title="S3 bucket prefix")):
    try:
        # build the image
        image_content = bytes(image.base64_content, encoding="ascii")
        image_content = b64decode(image_content)
        content_type = magic.from_buffer(image_content, mime=True)
        image_content = BytesIO(image_content)
    except Exception as e:
        raise ImageException(f'exception base64_content: {repr(e)}')
    url = path.join(prefix, image.filename)
    return {
        'image_url': c.upload(url, image_content, content_type)
    }


@app.delete("/items/")
def delete_file(filename: str, prefix: Optional[str] = Query('', title="S3 bucket prefix")):
    url = path.join(prefix, filename)
    return c.delete(url)
