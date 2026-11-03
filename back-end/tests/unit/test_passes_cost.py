import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from typing import Dict

from apis.REST.app import create_app
from database.models import Session, tollpasses


class passesCost(unittest.TestCase):
    """
    Class to mitigate a valid connection with the database
    Contains test cases for the /passesCost/ api call
    """

    def setUp(self) -> None:
        self.app = create_app().test_client()
        tollpasses.objects().delete()
        Session.objects().delete()

        login_data: Dict[str, str] = {
            "username": "admin",
            "password": "freepasses4all",
        }
        login_response = self.app.post("/api/login", json=login_data)
        token = login_response.get_json()["token"]
        self.headers = {"X-OBSERVATORY-AUTH": token}

    def tearDown(self) -> None:
        tollpasses.objects().delete()
        Session.objects().delete()

    def testing_passes_cost_1(self) -> None:
        passes_data: list[Dict[str, object]] = [
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
                "timestamp": "2022-01-04 00:12",
                "tollID": "NAO30",
                "tagRef": "MO5ZJA8DZ",
                "tagHomeID": "MO",
                "charge": 2.5,
            },
        ]

        response = self.app.post(
            "/api/admin/addpasses", json=passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.get("/api/passesCost/NAO/MO/20220101/20220104")
        self.assertEqual(response.status_code, 200)
        response = response.get_json()

        self.assertEqual(response["nPasses"], 2)
        self.assertEqual(response["passesCost"], 5)

    def testing_passes_cost_2(self) -> None:
        passes_data: list[Dict[str, object]] = [
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
                "timestamp": "2022-01-04 00:12",
                "tollID": "NAO30",
                "tagRef": "MO5ZJA8DZ",
                "tagHomeID": "MO",
                "charge": 2.5,
            },
        ]

        response = self.app.post(
            "/api/admin/addpasses", json=passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.get("/api/passesCost/NAO/MO/20220101/20220104")
        self.assertEqual(response.status_code, 200)
        response = response.get_json()

        self.assertEqual(response["nPasses"], 2)
        self.assertEqual(response["passesCost"], 5)

        response = self.app.get("/api/passesCost/NAO/NAO/20220101/20220104")
        self.assertEqual(response.status_code, 200)
        response = response.get_json()

        self.assertEqual(response["nPasses"], 2)
        self.assertEqual(response["passesCost"], 0)
