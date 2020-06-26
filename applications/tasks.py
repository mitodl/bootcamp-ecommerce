"""Tasks for applications"""
from applications import api
from main.celery import app


@app.task
def create_and_send_applicant_letter(application_id, *, letter_type):
    """Create and send an applicant letter"""
    from applications.models import BootcampApplication

    application = BootcampApplication.objects.get(id=application_id)
    api.create_and_send_applicant_letter(application, letter_type=letter_type)
