import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest

from apis.REST.app import create_app
from database.db import db
from database.models import Session


class TestUserLogout(unittest.TestCase):
    """
    Contains test cases for the /logout api call
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()

    def tearDown(self) -> None:
        Session.objects().delete()

    def test_user_logout(self) -> None:
        login_cred = {"username": "admin", "password": "freepasses4all"}

        response = self.app.post("/api/login", json=login_cred)
        token = response.get_json()["token"]

        self.headers = {"X-OBSERVATORY-AUTH": token}

        response = self.app.post("/api/logout", headers=self.headers)
        self.assertEqual(response.status_code, 204)

        session_in_db = Session.objects(token=token).first()
        self.assertIsNone(session_in_db)

    def test_missing_token(self) -> None:
        response = self.app.post("/api/logout")
        print(response.get_json())
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()

        expected = {"status": "failed", "info": "token missing"}

        self.assertEqual(response_json, expected)

    def test_invalid_token(self) -> None:
        login_cred = {"username": "admin", "password": "freepasses4all"}

        response = self.app.post("/api/login", json=login_cred)
        token = "123456"

        self.headers = {"X-OBSERVATORY-AUTH": token}

        response = self.app.post("/api/logout", headers=self.headers)
        self.assertEqual(response.status_code, 401)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "token invalid or already logged out"}

        self.assertEqual(response_json, expected)

    def test_token_with_no_user(self) -> None:
        token = "1321392132178"
        self.headers = {"X-OBSERVATORY-AUTH": token}

        response = self.app.post("/api/logout", headers=self.headers)
        self.assertEqual(response.status_code, 401)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "token invalid or already logged out"}

        self.assertEqual(response_json, expected)
