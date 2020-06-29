"""Tasks for applications"""
from applications.models import BootcampApplication
from applications import api
from main.celery import app


@app.task
def create_and_send_applicant_letter(application_id, *, letter_type):
    """Create and send an applicant letter"""
    from applications import mail_api

    application = BootcampApplication.objects.get(id=application_id)
    mail_api.create_and_send_applicant_letter(application, letter_type=letter_type)


@app.task
def populate_interviews_in_jobma(application_id):
    """Create an interview in Jobma and update our models with a link to the Jobma interview"""
    application = BootcampApplication.objects.get(id=application_id)
    api.populate_interviews_in_jobma(application)
