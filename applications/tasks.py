"""Tasks for applications"""
from applications import api
from applications.models import BootcampApplication
from main.celery import app


@app.task
def create_and_send_applicant_letter(application_id, *, is_acceptance):
    """Create and send an applicant letter"""
    application = BootcampApplication.objects.get(id=application_id)
    api.create_and_send_applicant_letter(application, is_acceptance=is_acceptance)
