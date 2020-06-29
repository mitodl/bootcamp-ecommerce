"""Tasks for applications"""
from applications.models import BootcampApplication
from main.celery import app


@app.task
def create_and_send_applicant_letter(application_id, *, letter_type):
    """Create and send an applicant letter"""
    from applications import mail_api

    application = BootcampApplication.objects.get(id=application_id)
    mail_api.create_and_send_applicant_letter(application, letter_type=letter_type)
