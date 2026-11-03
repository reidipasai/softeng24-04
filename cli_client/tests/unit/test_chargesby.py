import json
import os
import subprocess
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../back-end"))
)

import unittest
from typing import Dict

from apis.REST.app import create_app
from database.models import Session, tollpasses


class chargesBy(unittest.TestCase):
    """
    Class to mitigate a valid connection with the database.
    Contains test cases for the /chargesBy/ api call
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

    def testing_charges_by_1(self) -> None:
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

        response = (
            subprocess.run(
                "se2404 chargesby --opid NAO --from 20220101 --to 20220105 --format json",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            .stdout.strip("\n")
            .replace("'", '"')
        )

        json_output = json.loads(response)

        self.assertIn("vOpList", json_output)
        self.assertEqual(len(json_output["vOpList"]), 1)
        self.assertEqual(json_output["vOpList"][0]["visitingOpID"], "MO")
        self.assertEqual(json_output["vOpList"][0]["nPasses"], 2)
        self.assertEqual(json_output["vOpList"][0]["passesCost"], 5.0)

    def testing_chargs_by_2(self) -> None:
        passes_data: list[Dict[str, object]] = [
            {
                "timestamp": "2022-01-01 00:11",
                "tollID": "NAO30",
                "tagRef": "NAO5ZJA8DZ",
                "tagHomeID": "NAO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-01 00:15",
                "tollID": "NAO30",
                "tagRef": "NAO5ZJA8DZ",
                "tagHomeID": "NAO",
                "charge": 2.5,
            },
            {
                "timestamp": "2022-01-01 00:24",
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
                "timestamp": "2022-01-04 04:23",
                "tollID": "NAO25",
                "tagRef": "GGG3231231",
                "tagHomeID": "GGG",
                "charge": 20.0,
            },
            {
                "timestamp": "2022-01-05 00:13",
                "tollID": "NAO30",
                "tagRef": "FGH35424",
                "tagHomeID": "FGH",
                "charge": 5.6,
            },
            {
                "timestamp": "2022-01-05 01:23",
                "tollID": "NAO22",
                "tagRef": "KKMS23131",
                "tagHomeID": "KKM",
                "charge": 5.0,
            },
        ]

        response = self.app.post(
            "/api/admin/addpasses", json=passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = (
            subprocess.run(
                "se2404 chargesby --opid NAO --from 20220101 --to 20220105 --format json",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            .stdout.strip("\n")
            .replace("'", '"')
        )

        json_output = json.loads(response)

        self.assertEqual(len(json_output["vOpList"]), 4)
        self.assertEqual(json_output["vOpList"][0]["visitingOpID"], "MO")
        self.assertEqual(json_output["vOpList"][1]["visitingOpID"], "GGG")
        self.assertEqual(json_output["vOpList"][2]["visitingOpID"], "FGH")

        self.assertEqual(json_output["vOpList"][0]["passesCost"], 5.0)
        self.assertEqual(json_output["vOpList"][1]["passesCost"], 20.0)
