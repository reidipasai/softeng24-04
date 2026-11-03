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


class ResetStations(unittest.TestCase):
    """
    Class that contains test cases for the /admin/resetstations
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

    @patch("database.models.tollstations.save")
    def test_single_json(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data: Dict[str, object] = {
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

        response = self.app.post(
            "/api/admin/resetstations", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollstations.save")
    def test_list_json(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data_2: list[Dict[str, object]] = [
            {
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
            },
            {
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
            },
        ]

        response = self.app.post(
            "/api/admin/resetstations", json=self.passed_data_2, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollstations.save")
    def test_invalid_single_json(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data = {
            "OpID": "AM",
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

        response = self.app.post(
            "/api/admin/resetstations", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollstations.save")
    def test_invalid_single_json_2(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None
        self.passed_data = {
            "OpID": "AM",
            "TollId": "AM01",
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

        response = self.app.post(
            "/api/admin/resetstations", json=self.passed_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollstations.save")
    def test_invalid_single_csv(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """
            OpID,TollId,Name,PM,Locality,Road,Lat,Long,Email,Price1,Price2,Price3,Price4
            AM,AM01,Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα),ΜΤ,Ημαθίας-Κλειδί,Α/Δ Αθηνών-Θεσσαλονίκης,40.51974,22.57247,customercare@aegeanmotorway.gr,1.4,2,5.9,8.3
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/resetstations?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "400 BAD REQUEST")

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollstations.save")
    def test_valid_single_csv(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """OpID,Operator,TollID,Name,PM,Locality,Road,Lat,Long,Email,Price1,Price2,Price3,Price4
        AM,aegeanmotorway,AM01,Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα),ΜΤ,Ημαθίας-Κλειδί,Α/Δ Αθηνών-Θεσσαλονίκης,40.51974,22.57247,customercare@aegeanmotorway.gr,1.4,2,5.9,8.3
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/resetstations?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "200 OK")

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollstations.save")
    def test_invalid_single_csv_2(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """
            OpID,Name,PM,Locality,Road,Lat,Long,Email,Price1,Price2,Price3,Price4
            AM,AM01,Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα),ΜΤ,Ημαθίας-Κλειδί,Α/Δ Αθηνών-Θεσσαλονίκης,40.51974,22.57247,customercare@aegeanmotorway.gr,1.4,2,5.9,
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/resetstations?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "400 BAD REQUEST")

        response_json = response.get_json()
        expected = {"status": "failed", "info": "Passed data columns are not correct"}

        self.assertEqual(response_json, expected)

    @patch("database.models.tollstations.save")
    def test_valid_single_csv_2(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """OpID,Operator,TollID,Name,PM,Locality,Road,Lat,Long,Email,Price1,Price2,Price3,Price4
        AM,aegeanmotorway,AM01,Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα),ΜΤ,Ημαθίας-Κλειδί,Α/Δ Αθηνών-Θεσσαλονίκης,40.51974,22.57247,customercare@aegeanmotorway.gr,1.40,2.00,5.90,8.30
        AM,aegeanmotorway,AM02,Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Θεσσαλονίκη),ΜΤ,Ημαθίας-Κλειδί,Α/Δ Αθηνών-Θεσσαλονίκης,40.51943,22.57290,customercare@aegeanmotorway.gr,1.40,2.00,5.90,8.30
        AM,aegeanmotorway,AM03,Σταθμός Διοδίων Μακρυχωρίου Μετωπικά (Προς Αθήνα),ΜΤ,Λάρισας-Μακρυχώρι,Α/Δ Αθηνών-Θεσσαλονίκης,39.80461,22.50252,customercare@aegeanmotorway.gr,1.60,2.20,6.80,9.60
        AM,aegeanmotorway,AM04,Σταθμός Διοδίων Μακρυχωρίου Μετωπικά (Προς Θεσσαλονίκη),ΜΤ,Λάρισας-Μακρυχώρι,Α/Δ Αθηνών-Θεσσαλονίκης,39.80427,22.50270,customercare@aegeanmotorway.gr,1.60,2.20,6.80,9.60
        AM,aegeanmotorway,AM05,Σταθμός Διοδίων Μοσχοχωρίου Μετωπικά (Προς Αθήνα),ΜΤ,Λάρισας-Μοσχοχώρι,Α/Δ Αθηνών-Θεσσαλονίκης,39.52294,22.55670,customercare@aegeanmotorway.gr,2.50,3.60,10.80,15.10
        AM,aegeanmotorway,AM06,Σταθμός Διοδίων Μοσχοχωρίου Μετωπικά (Προς Θεσσαλονίκη),ΜΤ,Λάρισας-Μοσχοχώρι,Α/Δ Αθηνών-Θεσσαλονίκης,39.52292,22.55705,customercare@aegeanmotorway.gr,2.50,3.60,10.80,15.10
        AM,aegeanmotorway,AM07,Σταθμός Διοδίων Λεπτοκαρυάς Μετωπικά (Προς Αθήνα),ΜΤ,Πιερίας-Λεπτοκαρυά,Α/Δ Αθηνών-Θεσσαλονίκης,40.03581,22.56973,customercare@aegeanmotorway.gr,2.00,2.80,8.60,12.00
        AM,aegeanmotorway,AM08,Σταθμός Διοδίων Λεπτοκαρυάς Μετωπικά (Προς Θεσσαλονίκη),ΜΤ,Πιερίας-Λεπτοκαρυά,Α/Δ Αθηνών-Θεσσαλονίκης,40.03565,22.56999,customercare@aegeanmotorway.gr,2.00,2.80,8.60,12.00
        AM,aegeanmotorway,AM09,Σταθμός Διοδίων Πελασγίας Μετωπικά (Προς Αθήνα),ΜΤ,Φθιώτιδος-Πελασγία,Α/Δ Αθηνών-Θεσσαλονίκης,38.92051,22.84637,customercare@aegeanmotorway.gr,2.20,3.10,9.40,13.10
        AM,aegeanmotorway,AM10,Σταθμός Διοδίων Πελασγίας Μετωπικά (Προς Θεσσαλονίκη),ΜΤ,Φθιώτιδος-Πελασγία,Α/Δ Αθηνών-Θεσσαλονίκης,38.92015,22.84633,customercare@aegeanmotorway.gr,2.20,3.10,9.40,13.10
        AM,aegeanmotorway,AM11,Σταθμός Διοδίων Γυρτώνης Πλευρικά (Από Αθήνα),ΠΛ,Λάρισας-Γυρτώνη,Α/Δ Αθηνών-Θεσσαλονίκης,39.74348,22.47595,customercare@aegeanmotorway.gr,0.40,0.60,1.90,2.70
        AM,aegeanmotorway,AM12,Σταθμός Διοδίων Γυρτώνης Πλευρικά (Προς Αθήνα),ΠΛ,Λάρισας-Γυρτώνη,Α/Δ Αθηνών-Θεσσαλονίκης,39.74499,22.47529,customercare@aegeanmotorway.gr,0.40,0.60,1.90,2.70
        AM,aegeanmotorway,AM13,Σταθμός Διοδίων Ευαγγελισμού Πλευρικά (Από Θεσσαλονίκη),ΠΛ,Λάρισας-Ευαγγελισμός,Α/Δ Αθηνών-Θεσσαλονίκης,39.82932,22.51144,customercare@aegeanmotorway.gr,0.70,1.10,3.20,4.50
        AM,aegeanmotorway,AM14,Σταθμός Διοδίων Ευαγγελισμού Πλευρικά (Προς Θεσσαλονίκη),ΠΛ,Λάρισας-Ευαγγελισμός,Α/Δ Αθηνών-Θεσσαλονίκης,39.82932,22.51359,customercare@aegeanmotorway.gr,0.70,1.10,3.20,4.50
        AM,aegeanmotorway,AM15,Σταθμός Διοδίων Κιλελέρ Πλευρικά (Από Αθήνα),ΠΛ,Λάρισας-Κιλελέρ,Α/Δ Αθηνών-Θεσσαλονίκης,39.49450,22.62619,customercare@aegeanmotorway.gr,1.50,2.10,6.40,9.00
        AM,aegeanmotorway,AM16,Σταθμός Διοδίων Κιλελέρ Πλευρικά (Προς Αθήνα),ΠΛ,Λάρισας-Κιλελέρ,Α/Δ Αθηνών-Θεσσαλονίκης,39.49332,22.61891,customercare@aegeanmotorway.gr,1.50,2.10,6.40,9.00
        AM,aegeanmotorway,AM17,Σταθμός Διοδίων Μακρυχωρίου Πλευρικά (Από Αθήνα),ΠΛ,Λάρισας-Μακρυχώρι,Α/Δ Αθηνών-Θεσσαλονίκης,39.79680,22.49904,customercare@aegeanmotorway.gr,0.70,1.00,3.00,4.20
        AM,aegeanmotorway,AM18,Σταθμός Διοδίων Μεγάλου Μοναστηρίου Πλευρικά (Από Αθήνα),ΠΛ,Λάρισας-Μεγάλο Μοναστήρι,Α/Δ Αθηνών-Θεσσαλονίκης,39.44227,22.68931,customercare@aegeanmotorway.gr,1.20,1.70,5.00,7.00
        AM,aegeanmotorway,AM19,Σταθμός Διοδίων Μεγάλου Μοναστηρίου Πλευρικά (Προς Αθήνα),ΠΛ,Λάρισας-Μεγάλο Μοναστήρι,Α/Δ Αθηνών-Θεσσαλονίκης,39.44117,22.68652,customercare@aegeanmotorway.gr,1.20,1.70,5.00,7.00
        AM,aegeanmotorway,AM20,Σταθμός Διοδίων Πυργετού Πλευρικά (Προς Αθήνα),ΠΛ,Λάρισας-Πυργετός,Α/Δ Αθηνών-Θεσσαλονίκης,39.90926,22.62438,customercare@aegeanmotorway.gr,1.00,1.50,4.50,6.30
        AM,aegeanmotorway,AM21,Σταθμός Διοδίων Πυργετού Πλευρικά (Προς Θεσσαλονίκη),ΠΛ,Λάρισας-Πυργετός,Α/Δ Αθηνών-Θεσσαλονίκης,39.90894,22.62438,customercare@aegeanmotorway.gr,1.00,1.50,4.50,6.30
        AM,aegeanmotorway,AM22,Σταθμός Διοδίων Βελεστίνου Πλευρικά (Από Αθήνα),ΠΛ,Μαγνησίας-Βελεστίνο,Α/Δ Αθηνών-Θεσσαλονίκης,39.38855,22.76817,customercare@aegeanmotorway.gr,0.80,1.10,3.30,4.60
        AM,aegeanmotorway,AM23,Σταθμός Διοδίων Βελεστίνου Πλευρικά (Προς Αθήνα),ΠΛ,Μαγνησίας-Βελεστίνο,Α/Δ Αθηνών-Θεσσαλονίκης,39.38900,22.76446,customercare@aegeanmotorway.gr,0.80,1.10,3.30,4.60
        AM,aegeanmotorway,AM24,Σταθμός Διοδίων Βελεστίνου Πλευρικά (Προς Αθήνα),ΠΛ,Μαγνησίας-Βελεστίνο,Α/Δ Αθηνών-Θεσσαλονίκης,39.39075,22.76492,customercare@aegeanmotorway.gr,0.80,1.10,3.30,4.60
        AM,aegeanmotorway,AM25,Σταθμός Διοδίων Λεπτοκαρυάς Πλευρικά (Από Θεσσαλονίκη),ΠΛ,Πιερίας-Λεπτοκαρυά,Α/Δ Αθηνών-Θεσσαλονίκης,40.04498,22.56406,customercare@aegeanmotorway.gr,1.10,1.60,4.90,6.80
        AM,aegeanmotorway,AM26,Σταθμός Διοδίων Λεπτοκαρυάς Πλευρικά (Προς Θεσσαλονίκη),ΠΛ,Πιερίας-Λεπτοκαρυά,Α/Δ Αθηνών-Θεσσαλονίκης,40.04503,22.56537,customercare@aegeanmotorway.gr,1.10,1.60,4.90,6.80
        AM,aegeanmotorway,AM27,Σταθμός Διοδίων Πλαταμώνα Πλευρικά (Από Αθήνα),ΠΛ,Πιερίας-Πλαταμώνας,Α/Δ Αθηνών-Θεσσαλονίκης,39.98173,22.62521,customercare@aegeanmotorway.gr,0.40,0.60,1.80,2.50
        AM,aegeanmotorway,AM28,Σταθμός Διοδίων Πλαταμώνα Πλευρικά (Προς Αθήνα),ΠΛ,Πιερίας-Πλαταμώνας,Α/Δ Αθηνών-Θεσσαλονίκης,39.98173,22.62488,customercare@aegeanmotorway.gr,0.40,0.60,1.80,2.50
        AM,aegeanmotorway,AM29,Σταθμός Διοδίων Γλύφας Πλευρικά (Από Θεσσαλονίκη),ΠΛ,Φθιώτιδος-Γλύφα,Α/Δ Αθηνών-Θεσσαλονίκης,38.94941,22.87566,customercare@aegeanmotorway.gr,1.60,2.30,6.90,9.60
        AM,aegeanmotorway,AM30,Σταθμός Διοδίων Γλύφας Πλευρικά (Προς Θεσσαλονίκη),ΠΛ,Φθιώτιδος-Γλύφα,Α/Δ Αθηνών-Θεσσαλονίκης,38.94799,22.87658,customercare@aegeanmotorway.gr,1.60,2.30,6.90,9.60
        EG,egnatia,EG01,Σταθμός Διοδίων Σήραγγας Ακτίου Μετωπικά (Προς Αγρίνιο),ΜΤ,Αιτωλοακαρνανίας-Άκτιο,Ακτίου-Πρέβεζας,38.94008,20.76598,eoae@egnatia.gr,0.70,3.00,7.50,10.50
        EG,egnatia,EG02,Σταθμός Διοδίων Σήραγγας Ακτίου Μετωπικά (Προς Πρέβεζα),ΜΤ,Αιτωλοακαρνανίας-Άκτιο,Ακτίου-Πρέβεζας,38.94000,20.76634,eoae@egnatia.gr,0.70,3.00,7.50,10.50
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/resetstations?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.status, "200 OK")

        response_json = response.get_json()
        expected = {"status": "OK"}

        self.assertEqual(response_json, expected)


class ResetStationsInvalidUser(unittest.TestCase):
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

    @patch("database.models.tollstations.save")
    def test_valid_single_csv(self, mock_save: MagicMock) -> None:
        mock_save.return_value = None

        csv_data = """OpID,Operator,TollID,Name,PM,Locality,Road,Lat,Long,Email,Price1,Price2,Price3,Price4
        AM,aegeanmotorway,AM01,Σταθμός Διοδίων Κλειδίου Μετωπικά (Προς Αθήνα),ΜΤ,Ημαθίας-Κλειδί,Α/Δ Αθηνών-Θεσσαλονίκης,40.51974,22.57247,customercare@aegeanmotorway.gr,1.4,2,5.9,8.3
        """
        csv_file = BytesIO(csv_data.encode("utf-8"))

        response = self.app.post(
            "/api/admin/resetstations?format=csv",
            data=csv_file.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )

        self.assertEqual(response.get_json()["info"], "Access denied")
        self.assertEqual(response.get_json()["status"], "failed")
