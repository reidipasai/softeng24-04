import json
import os
import subprocess
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from typing import Dict
from unittest.mock import MagicMock, patch

from apis.REST.app import create_app
from database.models import Session, tollpasses


class passAnalysis(unittest.TestCase):
    """
    Class to mitigate a valid connection with the database
    Contains test cases for the /passAnalysis/ api call
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

    def tearDown(self) -> None:
        Session.objects().delete()
        tollpasses.objects().delete()

    @patch("database.models.tollpasses")
    def testing_pass_analysis_2(self, mock_tollpasses: MagicMock) -> None:
        mock_tollpasses.objects.return_value.count.return_value = 1

        self.passes_data: list[Dict[str, object]] = [
            {
                "timestamp": "2022-01-01 00:24",
                "tollID": "NAO30",
                "tagRef": "NAO5ZJA8DZ",
                "tagHomeID": "NAO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-01 00:23",
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
            {
                "timestamp": "2022-01-04 00:12",
                "tollID": "NAO30",
                "tagRef": "ANO5ZJA8DZ",
                "tagHomeID": "ANO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-03 00:12",
                "tollID": "NAO30",
                "tagRef": "MO5ZJA8DZ",
                "tagHomeID": "MO",
                "charge": 2.5,
            },
        ]

        response = self.app.post(
            "/api/admin/addpasses", json=self.passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

        response = (
            subprocess.run(
                "se2404 passanalysis --stationop NAO --tagop MO --from 20220101 --to 20220103 --format json",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            .stdout.strip("\n")
            .replace("'", '"')
        )

        json_output = json.loads(response)

        self.assertEqual(json_output["nPasses"], 2)
        self.assertEqual(json_output["passList"][0]["passCharge"], 2.5)
