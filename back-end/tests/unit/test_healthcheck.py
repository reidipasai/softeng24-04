import os
import sys
from typing import Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from unittest.mock import MagicMock, patch

from apis.REST.app import create_app
from database.models import Session, tollpasses, tollstations


class HealthCheckValid(unittest.TestCase):
    """
    Class to mitigate a valid connection with the database
    Contains test cases for the /admin/healthcheck api call
    """

    def setUp(self) -> None:
        self.app = create_app().test_client()
        tollstations.objects().delete()
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
        self.app.post("/api/admin/resetpasses", json={}, headers=self.headers)

    @patch("database.models.tollstations")
    @patch("database.models.tollpasses")
    def testing_healthcheck_1(
        self, mock_tollstations: MagicMock, mock_tollpasses: MagicMock
    ) -> None:
        mock_tollstations.objects.return_value.count.return_value = 1
        mock_tollpasses.objects.return_value.count.return_value = 1
        self.tollstations_data: Dict[str, object] = {
            "OpID": "AM",
            "Operator": "aegeanmotorway",
            "TollID": "AM01",
            "Name": "Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα)",
            "PM": "ΜΤ",
            "Locality": "Ημαθίας-Κλειδί",
            "Road": "Α/Δ Αθηνών-Θεσσαλονίκης",
            "Lat": 40.51974,
            "Long": 22.57247,
            "Email": "customercare@aegeanmotorway.gr",
            "Price1": 1.4,
            "Price2": 2,
            "Price3": 5.9,
            "Price4": 8.3,
        }

        self.passes_data: Dict[str, object] = {
            "timestamp": "2022-01-01 00:23",
            "tollID": "NAO30",
            "tagRef": "NAO5ZJA8DZ",
            "tagHomeID": "NO",
            "charge": 2.5,
        }

        response = self.app.post(
            "/api/admin/resetstations",
            json=self.tollstations_data,
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.post(
            "/api/admin/addpasses", json=self.passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

        response = self.app.get("/api/admin/healthcheck", headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = response.get_json()

        expected = {
            "status": "OK",
            "dbconnection": "Connected",
            "n_stations": 1,
            "n_tags": 1,
            "n_passes": 1,
        }

        self.assertEqual(response, expected)

    @patch("database.models.tollstations")
    @patch("database.models.tollpasses")
    def testing_healthcheck_2(
        self, mock_tollstations: MagicMock, mock_tollpasses: MagicMock
    ) -> None:
        mock_tollstations.objects.return_value.count.return_value = 1
        mock_tollpasses.objects.return_value.count.return_value = 1
        self.stations_data: Dict[str, object] = {
            "OpID": "AM",
            "Operator": "aegeanmotorway",
            "TollID": "AM01",
            "Name": "Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα)",
            "PM": "ΜΤ",
            "Locality": "Ημαθίας-Κλειδί",
            "Road": "Α/Δ Αθηνών-Θεσσαλονίκης",
            "Lat": 40.51974,
            "Long": 22.57247,
            "Email": "customercare@aegeanmotorway.gr",
            "Price1": 1.4,
            "Price2": 2,
            "Price3": 5.9,
            "Price4": 8.3,
        }

        self.passes_data: Dict[str, object] = {
            "timestamp": "2022-01-01 00:23",
            "tollID": "NAO30",
            "tagRef": "NAO5ZJA8DZ",
            "tagHomeID": "NO",
            "charge": 2.5,
        }

        response = self.app.post(
            "/api/admin/resetstations", json=self.stations_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.post(
            "/api/admin/addpasses", json=self.passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

        response = self.app.get("/api/admin/healthcheck", headers=self.headers)
        self.assertEqual(response.status_code, 200)

        response = response.get_json()

        expected = {
            "status": "OK",
            "dbconnection": "Connected",
            "n_stations": 1,
            "n_tags": 1,
            "n_passes": 1,
        }

        self.assertEqual(response, expected)


class HealthCheckInvalid(unittest.TestCase):
    """
    Class to mitigate a failing connection with the database
    Contains test cases for the /admin/healthcheck api call
    """

    def setUp(self) -> None:
        self.app = create_app().test_client()
        tollstations.objects().delete()
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
        self.app.post("/api/admin/resetpasses", json={}, headers=self.headers)

    @patch("database.models.tollstations.objects")  # Mock the database connection
    @patch("database.models.tollpasses.objects")
    def test_healthcheck_db_down(self, mock_db_tollstations, mock_db_tollpasses):
        mock_db_tollstations.side_effect = Exception("Database not connected")
        mock_db_tollpasses.side_effect = Exception("Database not connected")

        response = self.app.get("/api/admin/healthcheck", headers=self.headers)
        self.assertEqual(response.status_code, 500)

        response_data = response.get_json()

        expected = {
            "status": "failed",
            "dbconnection": "Failed - Database not connected",
        }

        self.assertEqual(response_data, expected)


class HealthCheckInvalidUser(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app().test_client()
        tollstations.objects().delete()
        tollpasses.objects().delete()
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

    @patch("database.models.tollstations")
    @patch("database.models.tollpasses")
    def test_healthcheck_employeecall(
        self, mock_tollstations: MagicMock, mock_tollpasses: MagicMock
    ) -> None:
        mock_tollstations.objects.return_value.count.return_value = 1
        mock_tollpasses.objects.return_value.count.return_value = 1

        self.stations_data: Dict[str, object] = {
            "OpID": "AM",
            "Operator": "aegeanmotorway",
            "TollID": "AM01",
            "Name": "Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα)",
            "PM": "ΜΤ",
            "Locality": "Ημαθίας-Κλειδί",
            "Road": "Α/Δ Αθηνών-Θεσσαλονίκης",
            "Lat": 40.51974,
            "Long": 22.57247,
            "Email": "customercare@aegeanmotorway.gr",
            "Price1": 1.4,
            "Price2": 2,
            "Price3": 5.9,
            "Price4": 8.3,
        }

        self.passes_data: Dict[str, object] = {
            "timestamp": "2022-01-01 00:23",
            "tollID": "NAO30",
            "tagRef": "NAO5ZJA8DZ",
            "tagHomeID": "NO",
            "charge": 2.5,
        }

        response = self.app.post(
            "/api/admin/resetstations", json=self.stations_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 401)

        response = self.app.post(
            "/api/admin/addpasses", json=self.passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 401)

        response = self.app.get("/api/admin/healthcheck", headers=self.headers)
        self.assertEqual(response.status_code, 401)
