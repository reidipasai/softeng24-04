import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from io import BytesIO
from typing import Dict
from unittest.mock import MagicMock, patch

from apis.REST.app import create_app
from database.db import db
from database.models import Session


class AddPasses(unittest.TestCase):
    """
    Class that contains test cases for the /admin/addpasses
    api call
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
        token = login_response.get_json()["token"]
        self.headers = {"X-OBSERVATORY-AUTH": token}

    def tearDown(self) -> None:
        Session.objects().delete()

    @patch("database.models.tollpasses.save")
    def test_single_json(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data: Dict[str, object] = {
            "timestamp": "2022-01-01 00:23",
            "tollID": "NAO30",
            "tagRef": "NAO5ZJA8DZ",
            "tagHomeID": "NO",
            "charge": 2.5,
        }

        response = self.app.post(
            "/api/admin/addpasses", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollpasses.save")
    def test_list_json(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data_2: list[Dict[str, object]] = [
            {
                "timestamp": "2022-01-01 00:23",
                "tollID": "NAO30",
                "tagRef": "NAO5ZJA8DZ",
                "tagHomeID": "NO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-01 00:23",
                "tollID": "NAO30",
                "tagRef": "NAO5ZJA8DZ",
                "tagHomeID": "NO",
                "charge": 2.5,
            },
        ]

        response = self.app.post(
            "/api/admin/addpasses", json=self.passed_data_2, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollpasses.save")
    def test_invalid_single_json(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data = {
            "timestam": "2022-01-01 00:23",
            "tollID": "NAO30",
            "tagRef": "NAO5ZJA8DZ",
            "tagHomeID": "NO",
            "charge": 2.5,
        }

        response = self.app.post(
            "/api/admin/addpasses", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollpasses.save")
    def test_invalid_single_json_2(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data = {
            "tollID": "NAO30",
            "tagRef": "NAO5ZJA8DZ",
            "tagHomeID": "NO",
            "charge": 2.5,
        }

        response = self.app.post(
            "/api/admin/addpasses", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollpasses.save")
    def test_invalid_single_csv(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """
            timestam,tollID,tagRef,tagHomeID,charge
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/addpasses?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "400 BAD REQUEST")

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollpasses.save")
    def test_valid_single_csv(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """
            timestamp,tollID,tagRef,tagHomeID,charge
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/addpasses?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "200 OK")

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollpasses.save")
    def test_invalid_single_csv_2(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """
            tollID,tagRef,tagHomeID,charge
            NAO30,NAO5ZJA8DZ,NO,2.5
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/addpasses?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "400 BAD REQUEST")

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollpasses.save")
    def test_valid_single_csv_2(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """
            timestamp,tollID,tagRef,tagHomeID,charge
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
            2022-01-01 00:23,NAO30,NAO5ZJA8DZ,NO,2.5
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/addpasses?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "200 OK")

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)


class AddPassesInvalidUser(unittest.TestCase):
    """
    Class that tries to use the /admin/addpasses API call
    without correct privileges.
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()

        login_data: Dict[str, str] = {
            "username": "user",
            "password": "notfreepasses4all",
        }
        login_response = self.app.post("/api/login", json=login_data)
        token = login_response.get_json()["token"]
        self.headers = {"X-OBSERVATORY-AUTH": token}

    def tearDown(self) -> None:
        self.app.post("/api/admin/resetpasses", json={}, headers=self.headers)

    @patch("database.models.tollpasses.save")
    def test_valid_single_csv(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """
            tollID,tagRef,tagHomeID,charge
            NAO30,NAO5ZJA8DZ,NO,2.5
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/addpasses?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.get_json()["info"], "Access denied")
        self.assertEqual(response.get_json()["status"], "failed")
