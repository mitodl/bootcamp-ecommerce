"""Ecommerce constants"""

# From secure acceptance documentation, under API reply fields:
# http://apps.cybersource.com/library/documentation/dev_guides/Secure_Acceptance_SOP/Secure_Acceptance_SOP.pdf
CYBERSOURCE_DECISION_ACCEPT = "ACCEPT"
CYBERSOURCE_DECISION_DECLINE = "DECLINE"
CYBERSOURCE_DECISION_REVIEW = "REVIEW"
CYBERSOURCE_DECISION_ERROR = "ERROR"
CYBERSOURCE_DECISION_CANCEL = "CANCEL"

# from https://developer.cybersource.com/library/documentation/dev_guides/CC_Svcs_SO_API/html/Topics/app_card_types.htm
CARD_TYPES = {
    "001": "Visa",
    "002": "Mastercard",  # or Eurocard
    "003": "American Express",
    "004": "Discover",
    "005": "Diners Club",
    "006": "Carte Blanche",
    "007": "JCB",
    "014": "EnRoute",
    "021": "JAL",
    "024": "Maestro",  # UK Domestic
    "031": "Delta",
    "033": "Visa Electron",
    "034": "Dankort",
    "036": "Cartes Bancaires",
    "037": "Carta Si",
    "039": "Encoded account number",
    "040": "UATP",
    "042": "Maestro",  # International
    "050": "Hipercard",
    "051": "Aura",
    "054": "Elo",
    "061": "RuPay",
    "062": "China UnionPay",
}


WIRE_TRANSFER_LEARNER_EMAIL = "Learner Email"
WIRE_TRANSFER_AMOUNT = "Amount"
WIRE_TRANSFER_ID = "Id"
WIRE_TRANSFER_BOOTCAMP_NAME = "Bootcamp Name"
WIRE_TRANSFER_BOOTCAMP_START_DATE = "Bootcamp Start Date"
WIRE_TRANSFER_BOOTCAMP_RUN_ID = "Bootcamp Run ID"
WIRE_TRANSFER_HEADER_FIELDS = [
    WIRE_TRANSFER_AMOUNT,
    WIRE_TRANSFER_LEARNER_EMAIL,
    WIRE_TRANSFER_ID,
    WIRE_TRANSFER_BOOTCAMP_RUN_ID,
    WIRE_TRANSFER_BOOTCAMP_NAME,
    WIRE_TRANSFER_BOOTCAMP_START_DATE,
]
