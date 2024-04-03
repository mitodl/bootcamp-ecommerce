"""Ecommerce celery tasks"""

from ecommerce import api
from main.celery import app


@app.task(acks_late=True)
def send_receipt_email(application_id):
    """Task to send a receipt email for an application"""
    api.send_receipt_email(application_id)
