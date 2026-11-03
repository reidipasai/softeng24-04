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

getpasses_bp = Blueprint("getpasses", __name__)


@getpasses_bp.route("/api/getpasses/<date_from>/<date_to>", methods=["GET"])  # type: ignore
def get_passes(date_from: str, date_to: str) -> Tuple[Any, int]:
    """
    Returns a json with all the passes in the database

    :date_from: str
    :date_to: str

    :rtype: Tuple[Any, int]
    """
    try:
        period_from = datetime.strptime(date_from, "%Y%m%d")
        period_to = (
            datetime.strptime(date_to, "%Y%m%d")
            + timedelta(days=1)
            - timedelta(seconds=1)
        )
        filtered_passes = tollpasses.objects(
            timestamp__gte=period_from, timestamp__lte=period_to
        ).order_by("timestamp")

        returned_json = {
            "total_passes": len(filtered_passes),
            "passes": filtered_passes,
        }

        response_format = request.args.get("format", "json").lower()

        if response_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(returned_json.keys())
            writer.writerow(returned_json.values())

            response = Response(output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = (
                "attachment; filename=get_stations.csv"
            )
            return response, 200
        else:
            return jsonify(returned_json), 200
    except Exception as e:
        logging.error(f"Error processing tollstations: {e}")
        return jsonify({"status": "failed", "info": "Internal server error"}), 500
