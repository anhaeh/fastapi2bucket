# encoding: utf-8
from fastapi.testclient import TestClient
from unittest import TestCase
from main import app


class BaseTest(TestCase):
    def setUp(self):
        self.client = TestClient(app)
