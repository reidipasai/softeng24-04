import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from typing import Dict
from unittest.mock import patch

from apis.REST.app import create_app
from database.models import Session, tollpasses


class passAnalysisInvalid(unittest.TestCase):
    """
    Class to mitigate a failing connection with the database
    Contains test cases for the /passAnalysis api call
    """

    def setUp(self) -> None:
        self.app = create_app().test_client()
        tollpasses.objects().delete()
        Session.objects().delete()
        self.maxDiff = None

        login_data: Dict[str, str] = {
            "username": "admin",
            "password": "freepasses4all",
        }
        login_response = self.app.post("/api/login", json=login_data)
        token = login_response.get_json()["token"]
        self.headers = {"X-OBSERVATORY-AUTH": token}

    @patch("database.models.tollpasses.objects")
    @patch("database.models.User.objects")
    @patch("database.models.Session.objects")
    def test_healthcheck_db_down(self, mock_tollpasses, mock_users, mock_sessions):
        mock_tollpasses.side_effect = Exception("Database not connected")
        mock_users.side_effect = Exception("Database not connected")
        mock_sessions.side_effect = Exception("Database not connected")

        self.passes_data: list[Dict[str, object]] = [
            {
                "timestamp": "2022-01-01 00:23",
                "tollID": "NAO30",
                "tagRef": "NAO5ZJA8DZ",
                "tagHomeID": "NAO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-01 00:24",
                "tollID": "NAO30",
                "tagRef": "NAO5ZJA8DZ",
                "tagHomeID": "NAO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-01 00:15",
                "tollID": "NAO25",
                "tagRef": "MO5ZJA8DZ",
                "tagHomeID": "MO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-04 00:11",
                "tollID": "NAO30",
                "tagRef": "MO5ZJA8DZ",
                "tagHomeID": "MO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-04 00:12",
                "tollID": "NAO30",
                "tagRef": "ANO5ZJA8DZ",
                "tagHomeID": "ANO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-03 00:14",
                "tollID": "NAO30",
                "tagRef": "MO5ZJA8DZ",
                "tagHomeID": "MO",
                "charge": 2.5,
            },
        ]

        response = self.app.post(
            "/api/admin/addpasses", json=self.passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 500)  # Expect failure

        # GET request for pass analysis
        response = self.app.get(
            "/api/passAnalysis/NAO/MO/20220101/20220103", headers=self.headers
        )
        self.assertEqual(response.status_code, 500)  # Expect failure

        # Validate response payload
        response_data = response.get_json()
        expected = {
            "status": "failed",
            "info": "Database not connected",
        }
        self.assertEqual(response_data, expected)
