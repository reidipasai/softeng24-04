import csv
import io
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database.models import tollpasses
from flask import Blueprint, Response, jsonify, request

passanalysis_bp = Blueprint("passanalysis", __name__)


@passanalysis_bp.route("/api/passAnalysis/<stationOpID>/<tagOpID>/<date_from>/<date_to>", methods=["GET"])  # type: ignore
def pass_analysis(
    stationOpID: str, tagOpID: str, date_from: str, date_to: str
) -> Tuple[Any, int]:
    """
    Returns a json with data about the total passes.

    :param tagOpID: The tag operator ID
    :type tagOpID: str
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
        returned_json = {
            "stationOpID": stationOpID,
            "tagOpID": tagOpID,
            "requestTimestamp": datetime.utcnow(),
            "periodFrom": period_from.isoformat(),
            "periodTo": period_to.isoformat(),
            "nPasses": 0,
            "passList": [],
        }
        filtered_passes = tollpasses.objects(
            tagHomeID=tagOpID,
            tollID__startswith=stationOpID,
            timestamp__gte=period_from,
            timestamp__lte=period_to,
        ).order_by("timestamp")

        pass_list = [
            {
                "passIndex": idx,
                "passID": 123213213,  # TODO, FIXME: We will ask about this
                "stationID": x.tollID,
                "timestamp": x.timestamp.isoformat(),
                "tagID": x.tagRef,
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
                "attachment; filename=pass_analysis.csv"
            )
            return response, 200
        else:
            return jsonify(returned_json), 200
    except Exception as e:
        logging.error(f"Error processing passes: {e}")
        return jsonify({"status": "failed", "info": f"{e}"}), 500
