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

chargesby_bp = Blueprint("chargesby", __name__)


@chargesby_bp.route("/api/chargesBy/<tollOpID>/<date_from>/<date_to>", methods=["GET"])  # type: ignore
def charges_by(tollOpID: str, date_from: str, date_to: str) -> Tuple[Any, int]:
    """
    Returns a json with data about the passes that happened from users with different
    tagOpID than tollOpID.

    :param tollOpID: the toll operator ID
    :type tollOpID: str
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
            "tollOpID": tollOpID,
            "requestTimestamp": datetime.utcnow(),
            "periodFrom": period_from.isoformat(),
            "periodTo": period_to.isoformat(),
            "vOpList": [],
        }

        ordered_passes = tollpasses.objects.order_by("timestamp")

        unique_op_ids = []
        seen_op_ids = set()

        for pass_data in ordered_passes:
            tagHomeID = pass_data.tagHomeID
            if tagHomeID not in seen_op_ids:
                unique_op_ids.append(tagHomeID)
                seen_op_ids.add(tagHomeID)

        for OpID in unique_op_ids:
            if OpID == tollOpID:
                continue
            filtered_passes = tollpasses.objects(
                tollID__startswith=tollOpID,
                tagHomeID=OpID,
                timestamp__gte=period_from,
                timestamp__lte=period_to,
            ).order_by("timestamp")

            passesCost = 0.0
            for x in filtered_passes:
                passesCost += x.charge

            returned_json["vOpList"].append(  # type: ignore
                {
                    "visitingOpID": OpID,
                    "nPasses": len(filtered_passes),
                    "passesCost": passesCost,
                }
            )

        response_format = request.args.get("format", "json").lower()

        if response_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(returned_json.keys())
            writer.writerow(returned_json.values())

            response = Response(output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = (
                "attachment; filename=charges_by.csv"
            )
            return response, 200
        else:
            return jsonify(returned_json), 200
    except Exception as e:
        logging.error(f"Error processing passes: {e}")
        return jsonify({"status": "failed", "info": f"{e}"}), 500


@chargesby_bp.route("/api/chargesBySpecific/<tollOpID>/<date_from>/<date_to>", methods=["GET"])  # type: ignore
def charges_by_specific(tollOpID: str, date_from: str, date_to: str) -> Tuple[Any, int]:
    """
    Returns a json with data about the passes that happened from users with different
    tagOpID than tollOpID.

    :param tollOpID: the toll operator ID
    :type tollOpID: str
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
            "tollOpID": tollOpID,
            "requestTimestamp": datetime.utcnow(),
            "periodFrom": period_from.isoformat(),
            "periodTo": period_to.isoformat(),
            "vOpList": [],
        }

        ordered_passes = tollpasses.objects.order_by("timestamp")

        unique_op_ids = []
        seen_op_ids = set()

        for pass_data in ordered_passes:
            tagHomeID = pass_data.tagHomeID
            if tagHomeID not in seen_op_ids:
                unique_op_ids.append(tagHomeID)
                seen_op_ids.add(tagHomeID)

        for OpID in unique_op_ids:
            if tollOpID.startswith(OpID):
                continue

            filtered_passes = tollpasses.objects(
                tollID=tollOpID,
                tagHomeID=OpID,
                timestamp__gte=period_from,
                timestamp__lte=period_to,
            ).order_by("timestamp")

            passesCost = 0.0
            for x in filtered_passes:
                passesCost += x.charge

            returned_json["vOpList"].append(  # type: ignore
                {
                    "visitingOpID": OpID,
                    "nPasses": len(filtered_passes),
                    "passesCost": passesCost,
                }
            )

        response_format = request.args.get("format", "json").lower()

        if response_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(returned_json.keys())
            writer.writerow(returned_json.values())

            response = Response(output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = (
                "attachment; filename=charges_by.csv"
            )
            return response, 200
        else:
            return jsonify(returned_json), 200
    except Exception as e:
        logging.error(f"Error processing passes: {e}")
        return jsonify({"status": "failed", "info": f"{e}"}), 500
