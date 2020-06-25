"""Constants for the mail app"""

EMAIL_VERIFICATION = "verification"
EMAIL_PW_RESET = "password_reset"
EMAIL_CHANGE_EMAIL = "change_email"
EMAIL_RECEIPT = "receipt"

EMAIL_TYPE_DESCRIPTIONS = {
    EMAIL_VERIFICATION: "Verify Email",
    EMAIL_PW_RESET: "Password Reset",
    EMAIL_CHANGE_EMAIL: "Change Email",
    EMAIL_RECEIPT: "Receipt Email",
}

MAILGUN_API_DOMAIN = "api.mailgun.net"

MAILGUN_DELIVERED = "delivered"
MAILGUN_FAILED = "failed"
MAILGUN_OPENED = "opened"
MAILGUN_CLICKED = "clicked"
MAILGUN_EVENTS = [MAILGUN_DELIVERED, MAILGUN_FAILED, MAILGUN_OPENED, MAILGUN_CLICKED]
MAILGUN_EVENT_CHOICES = [(event, event) for event in MAILGUN_EVENTS]
