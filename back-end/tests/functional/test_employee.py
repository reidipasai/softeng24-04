import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from io import BytesIO
from typing import Dict
from unittest.mock import MagicMock, patch

from apis.REST.app import create_app
from database.db import db
from database.models import Session, tollpasses, tollstations


class testEmployeeLogin(unittest.TestCase):
    """
    Class that contains tests for user of type `Employee` logging in
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()

    def tearDown(self) -> None:
        Session.objects().delete()

    def test_employee_login_json(self) -> None:
        """
        Registration for new user of role `Employee`
        """
        passed_data: Dict[str, str] = {
            "username": "user",
            "password": "wrongpassword",
        }

        response = self.app.post("/api/login", json=passed_data)
        self.assertEqual(response.status_code, 401)

        login_data: Dict[str, object] = {
            "username": "user",
            "password": "notfreepasses4all",
        }

        login_response = self.app.post("/api/login", json=login_data)
        self.assertEqual(login_response.status_code, 200)

        response_json = login_response.get_json()
        self.assertEqual(len(response_json), 1)

        self.token = Session.objects(username="user").first()

        self.assertIsNotNone(self.token)
        self.assertEqual(self.token.username, "user")

        token = login_response.get_json()["token"]
        headers = {"X-OBSERVATORY-AUTH": token}

        response = self.app.post("/api/logout", headers=headers)
        self.assertEqual(response.status_code, 204)

        session_in_db = Session.objects(token=token).first()
        self.assertIsNone(session_in_db)


class testEmployeeAttemptsToAddPasses(unittest.TestCase):
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


class EmployeeHealthCheckRestrictedUse(unittest.TestCase):
    """
    Class to show employees have no access to /admin/healthcheck
    """

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
        self.assertEqual(response.status_code, 401)

        response = self.app.post(
            "/api/admin/addpasses", json=self.passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 401)

        response = self.app.get("/api/admin/healthcheck", headers=self.headers)
        self.assertEqual(response.status_code, 401)
