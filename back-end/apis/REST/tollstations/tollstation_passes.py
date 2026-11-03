import csv
import io
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database.models import tollpasses, tollstations
from flask import Blueprint, Response, jsonify, request

tollstation_passes_bp = Blueprint("tollstation_passes", __name__)


@tollstation_passes_bp.route(
    "/api/tollStationPasses/<tollStationID>/<date_from>/<date_to>", methods=["GET"]
)  # type: ignore
def tollstation_passes(
    tollStationID: str, date_from: str, date_to: str
) -> Tuple[Any, int]:
    """
    Returns a json with data about the tollstation passes of the passed
    tollstation ID from date_from to date_to.

    :param tollStationID:  The ID of the passed toll station
    :type tollStationID: str
    :param date_from: starting date of search
    :type date_from: str
    :param date_to: ending date of search
    :type date_to: str
    :method: GET

    :rtype: Tuple[Any, int]
    """
    try:
        period_from = datetime.strptime(date_from, "%Y%m%d")
        period_to = (
            datetime.strptime(date_to, "%Y%m%d")
            + timedelta(days=1)
            - timedelta(seconds=1)
        )

        station_operator = tollstations.objects(TollID=tollStationID).first()

        if station_operator is None:
            return (
                jsonify(
                    {
                        "stationID": None,
                        "stationOperator": None,
                        "requestTimestamp": datetime.utcnow(),
                        "periodFrom": period_from.isoformat(),
                        "periodTo": period_to.isoformat(),
                        "nPasses": 0,
                        "passList": [],
                    }
                ),
                200,
            )

        filtered_passes = tollpasses.objects(
            tollID=tollStationID, timestamp__gte=period_from, timestamp__lte=period_to
        ).order_by("timestamp")

        returned_json = {
            "stationID": tollStationID,
            "stationOperator": tollstations.objects(TollID=tollStationID)
            .first()
            .Operator,
            "requestTimestamp": datetime.utcnow(),
            "periodFrom": period_from.isoformat(),
            "periodTo": period_to.isoformat(),
            "nPasses": 0,
            "passList": [],
        }

        pass_list = [
            {
                "passIndex": idx,
                "passID": str(x.id) if x.id else "NULL",
                "timestamp": x.timestamp.isoformat(),
                "tagID": x.tagRef,
                "tagProvider": tollstations.objects(TollID=x.tollID).first().OpID,
                "passType": (
                    "home"
                    if x.tagHomeID.startswith(
                        tollstations.objects(TollID=x.tollID).first().OpID
                    )
                    else "visitor"
                ),
                "passCharge": x.charge,
            }
            for (idx, x) in enumerate(filtered_passes)
        ]

        returned_json["nPasses"] = len(pass_list)
        returned_json["passList"] = pass_list

        response_format = request.args.get("format", "json").lower()

        if response_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(returned_json.keys())
            writer.writerow(returned_json.values())

            response = Response(output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = (
                "attachment; filename=tollstation_passes.csv"
            )
            return response, 200
        else:
            return jsonify(returned_json), 200
    except Exception as e:
        logging.error(f"Error processing passes: {e}")
        return jsonify({"status": "falied", "info": e}), 500
