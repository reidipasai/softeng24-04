from typing import Dict

import numpy as np
import requests  # type: ignore

BASE_URL = "http://127.0.0.1:9115"

Companies = ["AM", "EG", "GE", "KO", "MO", "NAO", "NO", "OO"]


def calc_owe(toll: str, datefrom: str, dateto: str) -> Dict[str, float]:
    url = f"{BASE_URL}/api/chargesBy/{toll}/{datefrom}/{dateto}?format=json"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch company data")
        return {}

    charges_data = response.json()

    costs = {}
    for entry in charges_data.get("vOpList", []):
        visitingOpID = entry["visitingOpID"]
        passesCost = entry["passesCost"]
        costs[visitingOpID] = passesCost

    return costs


def calculate_matrix(datefrom: str, dateto: str) -> np.ndarray:
    costs_matrix = np.zeros((8, 8))
    company_index = {company: idx for idx, company in enumerate(Companies)}

    for toll in Companies:
        cost_data = calc_owe(toll, datefrom, dateto)
        toll_idx = company_index[toll]

        for tag, cost in cost_data.items():
            tag_idx = company_index[tag]
            costs_matrix[tag_idx][toll_idx] = cost

    return costs_matrix
