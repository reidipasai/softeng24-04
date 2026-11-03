import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from typing import Dict

from apis.REST.app import create_app
from database.db import db
from database.models import Session


class TestUserLogin(unittest.TestCase):
    """
    Class that contains test cases for the /login
    api call
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()

    def tearDown(self) -> None:
        Session.objects().delete()

    # @patch("database.models.User.save")
    # @patch("database.models.Session.save")
    def test_user_login(self) -> None:
        # mock_user.objects.return_value = None
        # mock_session.objects.return_value = None

        passed_data: Dict[str, object] = {
            "username": "admin",
            "password": "freepasses4all",
        }

        response = self.app.post("/api/login", json=passed_data)
        print(response.get_json())
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        self.assertEqual(len(response_json), 1)

        token_in_db = Session.objects(username="admin").first()

        self.assertIsNotNone(token_in_db)
        self.assertEqual(token_in_db.username, "admin")

    def test_invalid_username(self) -> None:
        passed_data: Dict[str, object] = {
            "username": "wronguser",
            "password": "adminpassword1",
        }

        response = self.app.post("/api/login", json=passed_data)

        self.assertEqual(response.status_code, 401)

        response_json = response.get_json()

        expected = {"status": "failed", "info": "Invalid credentials"}

        self.assertEqual(response_json, expected)

    def test_invalid_password(self) -> None:

        passed_data: Dict[str, str] = {
            "username": "admin",
            "password": "wrongpassword",
        }

        response = self.app.post("/api/login", json=passed_data)
        self.assertEqual(response.status_code, 401)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Invalid credentials"}

        self.assertEqual(response_json, expected)

    def test_missing_username(self) -> None:
        passed_data: Dict[str, str] = {"password": "freepasses4all"}

        response = self.app.post("/api/login", json=passed_data)

        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()

        expected = {
            "status": "failed",
            "info": "Passed data columns are not correct",
        }

        self.assertEqual(response_json, expected)

    def test_missing_password(self) -> None:
        passed_data: Dict[str, str] = {"username": "admin"}

        response = self.app.post("/api/login", json=passed_data)

        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()

        expected = {
            "status": "failed",
            "info": "Passed data columns are not correct",
        }

        self.assertEqual(response_json, expected)

    def test_extra_columns(self) -> None:
        passed_data: Dict[str, str] = {
            "username": "admin",
            "password": "freepasses4all",
            "extra_column": "unexpected_value",
        }

        response = self.app.post("/api/login", json=passed_data)

        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()

        expected = {
            "status": "failed",
            "info": "Passed data columns are not correct",
        }

        self.assertEqual(response_json, expected)

    def test_invalid_data_format(self) -> None:
        passed_data: Dict[str, str] = {"invalid_data_format": 0}

        response = self.app.post("/api/login", json=passed_data)

        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()

        expected = {
            "status": "failed",
            "info": "Passed data columns are not correct",
        }

        self.assertEqual(response_json, expected)
