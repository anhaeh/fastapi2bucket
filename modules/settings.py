# encoding: utf-8
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from os import environ


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_host: str
    region: str
    bucket_name: str
    cache_uri: Optional[str] = None


def get_setting():
    if environ.get('TESTING'):
        return Settings(
            aws_access_key_id='',
            aws_secret_access_key='',
            aws_host='',
            region='',
            bucket_name='test-bucket',
            cache_uri=None
        )
    return Settings()
