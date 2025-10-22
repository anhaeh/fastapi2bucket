# encoding: utf-8
from typing import Optional
from os import environ
from enum import Enum

from pydantic import BaseSettings, validator


class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_host: str
    region: str
    bucket_name: str
    cache_uri: Optional[str]
    environment: Environment = Environment.development

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("environment", pre=True, always=True)
    def validate_environment(cls, v):
        if v is None:
            return Environment.development
        if isinstance(v, Environment):
            return v
        try:
            return Environment(v)
        except ValueError:
            valid = ", ".join([e.value for e in Environment])
            raise ValueError(f"Invalid environment '{v}'. Valid values: {valid}")


def get_setting():
    if environ.get("TESTING"):
        return Settings(
            aws_access_key_id="",
            aws_secret_access_key="",
            aws_host="",
            region="",
            bucket_name="test-bucket",
            cache_uri=None,
            environment=Environment.testing,
        )
    return Settings()
