# FastApi2bucket

This is an api service built in fastApi framework to manipulate files
with Amazon S3's buckets. You can push, list and delete files.

This service has an internal cache for the lists objects. If you add 
or delete any file, this refresh the cache (considering the optional prefix).

For the moment, it has a redis client and a null client, but it could extend
with other cache clients (see cache.py).


`.env.sample` is an example configuration for the service.


## Install

    pip install -r requirements.txt

## Copy .env.sample and complete with your credentials

    cp .env.sample .env

## Run the app

    uvicorn main:app

## Run the app for development

    uvicorn main:app --reload

## Run tests

    python -m unittest discover


# REST API Docs (swagger ui)

`http://127.0.0.1:8000/docs`

# REST API

The REST API contains 3 endpoints, to list, upload and delete files.
All the endpoints has an optional query param `prefix`.

## Get service status

### Request

`GET /status/`

    curl -X 'GET' 'http://127.0.0.1:8000/status/' -H 'accept: application/json'

### Response
    {
      "status": "ok",
      "bucket_name": "my-bucket",
      "errors": [],
      "files_in_env": 65
    }


## Get list of Files

### Request

`GET /items/`

    curl -X 'GET' 'http://127.0.0.1:8000/items/' -H 'accept: application/json'

### Response
    [
        {
            "name":"my_file.txt",
            "url":"https://bucket.amazonaws.com/my_file.txt",
            "modified":"2019-05-15T20:22:08+00:00",
            "size": 269
        }
    ]

### Request with a prefix

`GET /items/?prefix=app-test`

    curl -X 'GET' 'http://127.0.0.1:8000/items/?prefix=app-test' -H 'accept: application/json'

### Response
    [
        {
            "name":"my_file.txt",
            "url":"https://bucket.amazonaws.com/app-test/my_file.txt",
            "modified":"2019-05-15T20:22:08+00:00",
            "size": 269
        }
    ]

## Upload a file

### Request

`POST /items/`

    curl -X 'POST' \
      'http://127.0.0.1:8000/items/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "base64_content": "TWFuIGlzIGRpc3Rpbmd1aXNoZWQsIG5vdCBvbmx5IGJ5IGhpcyByZWFzb24sIGJ1dCBieSB0aGlzIHNpbmd1bGFyIHBhc3Npb24gZnJvbSBvdGhlciBhbmltYWxzLCB3aGljaCBpcyBhIGx1c3Qgb2YgdGhlIG1pbmQsIHRoYXQgYnkgYSBwZXJzZXZlcmFuY2Ugb2YgZGVsaWdodCBpbiB0aGUgY29udGludWVkIGFuZCBpbmRlZmF0aWdhYmxlIGdlbmVyYXRpb24gb2Yga25vd2xlZGdlLCBleGNlZWRzIHRoZSBzaG9ydCB2ZWhlbWVuY2Ugb2YgYW55IGNhcm5hbCBwbGVhc3VyZS4=",
      "filename": "my_file.txt"
    }'

### Response

    { image_url": "https://bucket.s3.amazonaws.com/my_file.txt" }

## Delete a file

### Request

`DELETE /items/`

    curl -X 'DELETE' \
      'http://127.0.0.1:8000/items/?filename=my_file.txt' \
      -H 'accept: application/json'

### Response
    {
      "ResponseMetadata": {
        "RequestId": "xxxxxx",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
          "x-amz-id-2": "xxxxx",
          "x-amz-request-id": "xxxxx",
          "date": "Mon, 03 May 2021 17:33:31 GMT",
          "content-type": "application/xml",
          "transfer-encoding": "chunked",
          "server": "AmazonS3",
          "connection": "close"
        },
        "RetryAttempts": 0
      },
      "Deleted": [
        {
          "Key": "my_file.txt"
        }
      ]
    }
