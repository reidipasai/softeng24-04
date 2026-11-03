import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "apis")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "database")))

import unittest
from typing import Dict

from apis.REST.app import create_app
from database.db import db
from database.models import Session


class TestUserRegister(unittest.TestCase):
    """
    Contains test cases for the /register additional api call
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()

        login_data: Dict[str, str] = {
            "username": "admin",
            "password": "freepasses4all",
        }
        login_response = self.app.post("/api/login", json=login_data)
        self.token = login_response.get_json()["token"]
        self.headers = {"X-OBSERVATORY-AUTH": self.token}

    def test_user_register_json(self) -> None:
        self.passed_data: Dict[str, object] = {
            "username": "newuser",
            "password": "newpassword",
            "role": "Employee",
        }

        response = self.app.post(
            "/api/register", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    def test_user_register_csv(self) -> None:
        data = "username,password,role\nnewuser1,password1,Employee\nnewuser2,password2,Admin"
        headers = {"X-OBSERVATORY-AUTH": self.token, "Content-Type": "application/csv"}

        response = self.app.post("/api/register?format=csv", data=data, headers=headers)
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    def test_missing_columns_json(self) -> None:
        self.passed_data: Dict[str, object] = {
            "username": "newuser",
            "password": "newpassword",
        }

        response = self.app.post(
            "/api/register", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    def test_invalid_data_format_csv(self) -> None:
        data = "username,password,role,Extra\nnewuser,password,role,extra"
        headers = {"X-OBSERVATORY-AUTH": self.token, "Content-Type": "application/csv"}

        response = self.app.post("/api/register?format=csv", data=data, headers=headers)
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    def test_invalid_data_format_json(self) -> None:
        self.passed_data: Dict[str, object] = {
            "username": "newuser",
            "password": "newpassword",
            "role": "user",
            "Extra": "extra_data",
        }

        response = self.app.post(
            "/api/register", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()

        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    def test_missing_data_columns(self) -> None:
        self.passed_data: Dict[str, object] = {"username": "newuser", "role": "user"}

        response = self.app.post(
            "/api/register", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)
