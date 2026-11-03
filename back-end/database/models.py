from typing import Dict

from .db import db


class tollstations(db.Document):
    """
    Database model for the tollstations.
    A sample csv can be found at the shared/ folder
    """

    OpID = db.StringField(required=True)
    Operator = db.StringField(required=True)
    TollID = db.StringField(required=True, unique=True)
    Name = db.StringField(required=True)
    PM = db.StringField(required=True)
    Locality = db.StringField(required=True)
    Road = db.StringField(required=True)
    Lat = db.FloatField(required=True)
    Long = db.FloatField(required=True)
    Email = db.StringField(required=True)
    Price1 = db.FloatField(required=True)
    Price2 = db.FloatField(required=True)
    Price3 = db.FloatField(required=True)
    Price4 = db.FloatField(required=True)

    def to_json(self) -> Dict:
        return {
            "OpID": self.OpID,
            "Operator": self.Operator,
            "TollID": self.TollID,
            "Name": self.Name,
            "PM": self.PM,
            "Locality": self.Locality,
            "Road": self.Road,
            "Lat": self.Lat,
            "Long": self.Long,
            "Email": self.Email,
            "Price1": self.Price1,
            "Price2": self.Price2,
            "Price3": self.Price3,
            "Price4": self.Price4,
        }


class tollpasses(db.Document):
    """
    Database model for tollpasses.
    A sample can be found at the shared/ folder.
    """

    timestamp = db.DateTimeField(required=True)
    tollID = db.StringField(required=True)
    tagRef = db.StringField(required=True)
    tagHomeID = db.StringField(required=True)
    charge = db.FloatField(required=True)

    meta = {
        "indexes": [
            {
                "fields": ["timestamp", "tollID", "tagRef"],
                "unique": True,
            }
        ]
    }

    def to_json(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tollID": self.tollID,
            "tagRef": self.tagRef,
            "tagHomeID": self.tagHomeID,
            "charge": self.charge,
        }


class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    role = db.StringField(required=True, choices=["Admin", "Employee"])

    def to_json(self) -> Dict:
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role,
        }


class Session(db.Document):
    token = db.StringField(required=True, unique=True)
    username = db.StringField(required=True, unique=True)

    def to_json(self) -> Dict:
        return {
            "token": self.token,
            "username": self.username,
        }
