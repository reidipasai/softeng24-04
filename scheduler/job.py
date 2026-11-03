import time
from datetime import datetime, timedelta

import numpy as np

from .cost_matrix_calculator import calculate_matrix
from .email_sender import create_excel_file, send_email

REAL_TIMESTAMPS = [
    datetime.now().strftime("%Y%m%d"),
    (datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
]
TEST_TIMESTAMPS = [
    datetime(2022, 1, 1, 00, 00).strftime("%Y%m%d"),
    datetime(2022, 1, 31, 00, 00).strftime("%Y%m%d"),
]

Companies = [
    ("AM", "aegeanmotorway", "customercare@aegeanmotorway.gr"),
    ("EG", "egnatia", "eoae@egnatia.gr"),
    ("GE", "gefyra", "info@gefyra.gr"),
    ("KO", "kentrikiodos", "customercare@kentrikiodos.gr"),
    ("MO", "moreas", "info@moreas.com.gr"),
    ("NAO", "naodos", "customercare@attikesdiadromes.gr"),
    ("NO", "neaodos", "info@neaodos.gr"),
    ("OO", "olympiaodos", "customercare@olympiaoperation.gr"),
]


def job() -> None:
    print("Fetching data and sending emails...")

    matrix = calculate_matrix(TEST_TIMESTAMPS[0], TEST_TIMESTAMPS[1])

    print("Debt Matrix (8x8):")
    print(matrix)

    np.fill_diagonal(matrix, 0)
    company_debts = []

    for i, company in enumerate(Companies):
        __, company_name, _ = company
        debts = []

        for j in range(8):
            if i != j:
                debt_value = matrix[i, j]
                other_company_name = Companies[j][1]
                debts.append((other_company_name, debt_value))

        company_debts.append(debts)

    for i, company_debt_list in enumerate(company_debts):
        _, name, __ = Companies[i]

        excel_filepath = create_excel_file(name, company_debt_list)
        send_email(
            "reidipasai03@gmail.com",
            name,
            TEST_TIMESTAMPS[0],
            TEST_TIMESTAMPS[1],
            excel_filepath,  # TODO: We have to add toll's emails
        )

        time.sleep(2)  # Prevent spamming
