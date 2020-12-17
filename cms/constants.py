"""Constants for the CMS app"""
import pathlib


BOOTCAMP_INDEX_SLUG = "bootcamps"
SIGNATORY_INDEX_SLUG = "signatories"
CERTIFICATE_INDEX_SLUG = "certificate"

RESOURCES_DIRECTORY = pathlib.Path(__file__).absolute().parent / "resources"
ACCEPTANCE_DEFAULT_LETTER_TEXT = open(
    RESOURCES_DIRECTORY / "acceptance_letter.txt"
).read()
REJECTION_DEFAULT_LETTER_TEXT = open(
    RESOURCES_DIRECTORY / "rejection_letter.txt"
).read()

SAMPLE_DECISION_TEMPLATE_CONTEXT = {
    "first_name": "FirstName",
    "last_name": "LastName",
    "bootcamp_name": "Sample Bootcamp",
    "bootcamp_start_date": "July 1, 2136",
    "price": "$1987.65",
}
