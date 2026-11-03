import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import List, Tuple

import pandas as pd

email_sender = "softeng2404@gmail.com"
email_password = "hivdcomdkvmkukdk"


def create_excel_file(
    company_name: str, company_debt_list: List[Tuple[str, float]]
) -> str:
    """
    Creates an Excel file with the company's debt data.

    :param company_name: The name of the company (string).
    :param company_debt_list: A list of tuples, where each tuple contains
                               the company name (str) and the debt amount (float).
    :return: The file path where the Excel file is saved.
    """
    filename = f"{company_name}.xlsx"

    folder_path = "excel_files"
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, filename)

    debts_data = []

    for debt in company_debt_list:
        owed_to, debt_value = debt
        debts_data.append({"Owes to": owed_to, "Price": debt_value})

    df = pd.DataFrame(debts_data)
    df.to_excel(file_path, index=False)
    print(f"Excel file saved at: {file_path}")

    return file_path


def send_email(
    receiver: str, company_name: str, datefrom: str, dateto: str, attachment_path: str
) -> None:
    """
    Sends an email with an attachment to the specified receiver.

    :param receiver: The email address of the recipient (string).
    :param company_name: The name of the company (string).
    :param datefrom: The start date of the report (string).
    :param dateto: The end date of the report (string).
    :param attachment_path: The path of the file to attach (string).
    :return: None
    """
    try:
        body = f"Αξιότιμη {company_name},\n\nΣε συνέχεια της συνεργασίας μας για τη διαχείριση της διαλειτουργικότητας των ηλεκτρονικών διοδίων, σας αποστέλλουμε την οικονομική αναφορά της τρέχουσας εβδομάδας. Η αναφορά αυτή περιλαμβάνει συγκεντρωτικά στοιχεία για τις συναλλαγές που πραγματοποιήθηκαν μέσω του συστήματος, διευκολύνοντας την παρακολούθηση των οικονομικών εκκρεμοτήτων μεταξύ των εμπλεκόμενων εταιριών.\n\nΗ τακτική ενημέρωση των οικονομικών σας στοιχείων αποσκοπεί στη διευκόλυνση της οικονομικής διαχείρισης και της λογιστικής σας συμμόρφωσης, συμβάλλοντας σε μια πιο αποδοτική και διαφανή διαδικασία εκκαθάρισης.\n\nΓια οποιαδήποτε περαιτέρω πληροφορία ή διευκρίνιση, παραμένουμε στη διάθεσή σας.\n\nΜε εκτίμηση,\nTollSync"
        subject = (
            f"Εβδομαδιαία Οικονομική Αναφορά Οφειλών Διοδίων – {datefrom} εως {dateto}"
        )
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = receiver
        em["Subject"] = subject
        em.set_content(body)

        with open(attachment_path, "rb") as file:
            file_data = file.read()
            file_name = os.path.basename(attachment_path)
            em.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=file_name,
            )

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, receiver, em.as_string())

        print(f"Email sent to {company_name} with attachment '{file_name}'")
    except Exception as e:
        print(f"Failed to send email: {e}")
