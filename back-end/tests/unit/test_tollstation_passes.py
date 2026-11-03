import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from io import BytesIO
from typing import Dict

from apis.REST.app import create_app
from database.models import Session, tollpasses, tollstations


class tollStationPasses(unittest.TestCase):
    """
    Class to mitigate a valid connection with the database
    Contains test cases for the /tollStationPasses/ api call
    """

    def setUp(self) -> None:
        self.app = create_app().test_client()
        tollpasses.objects().delete()
        tollstations.objects().delete()
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
        tollstations.objects().delete()
        Session.objects().delete()

    def testing_tollstation_passes_1(self) -> None:
        tollstations_data = """OpID,Operator,TollID,Name,PM,Locality,Road,Lat,Long,Email,Price1,Price2,Price3,Price4
        NAO,naodos,NAO30,Σταθμός Διοδίων Αθηνών-Λαμίας Πλευρικά (Από Λαμία Προς Ελευσίνα),ΜΤ,Αττικής-Μεταμόρφωση,Αττική Οδός,38.06315,23.74873,customercare@attikesdiadromes.gr,1.25,2.50,6.25,10.00
        NAO,naodos,NAO25,Σταθμός Διοδίων Λεωφ. Κηφισίας Πλευρικά (Προς Αεροδρόμιο),ΜΤ,Αττικής-Μαρούσι,Αττική Οδός,38.04123,23.80530,customercare@attikesdiadromes.gr,1.25,2.50,6.25,10.00
        KO,kentrikiodos,KO14,Σταθμός Διοδίων Προαστίου Πλευρικά (Προς Λαμία),ΠΛ,Καρδίτσας-Προάστιο,Α/Δ Λαμίας-Τρικάλων,39.47460,21.90324,customercare@kentrikiodos.gr,0.80,1.15,2.85,4.05
        """
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
            {
                "timestamp": "2022-01-04 00:13",
                "tollID": "KO14",
                "tagRef": "KO3243423432",
                "tagHomeID": "KO",
                "charge": 3.5,
            },
        ]
        response = self.app.post(
            "/api/admin/addpasses", json=passes_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        tollstations_data = BytesIO(tollstations_data.encode("utf-8"))
        response = self.app.post(
            "/api/admin/resetstations?format=csv",
            data=tollstations_data.getvalue(),
            content_type="text/csv",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.get("/api/tollStationPasses/NAO30/20220101/20220101")
        self.assertEqual(response.status_code, 200)
        response = response.get_json()
        self.assertEqual(response["nPasses"], 2)
        self.assertEqual(response["passList"][0]["tagProvider"], "NAO")
        self.assertEqual(response["passList"][1]["passType"], "home")
        self.assertEqual(response["passList"][0]["passCharge"], 2.5)

        add_pass = {
            "timestamp": "2022-01-01 01:12",
            "tollID": "NAO30",
            "tagRef": "MO23123",
            "tagHomeID": "MO",
            "charge": 3.5,
        }
        response = self.app.post(
            "/api/admin/addpasses", json=add_pass, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.get(
            "/api/tollStationPasses/NAO30/20220101/20220101"
        ).get_json()
        self.assertEqual(response["passList"][2]["passType"], "visitor")
