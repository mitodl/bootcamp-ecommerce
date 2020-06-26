"""Mail views"""
from datetime import timedelta

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from mail.v2 import api
from mail.v2.constants import EMAIL_RECEIPT, EMAIL_PW_RESET, EMAIL_VERIFICATION
from mail.forms import EmailDebuggerForm
from main.utils import now_in_utc


def drf_datetime(dt):
    """
    Returns a datetime formatted as a DRF DateTimeField formats it

    Args:
        dt(datetime): datetime to format

    Returns:
        str: ISO 8601 formatted datetime
    """
    return dt.isoformat().replace("+00:00", "Z")


def _render_email(email_type):
    """Render the email with dummy data"""
    context = api.get_base_context()

    # static, dummy data
    if email_type == EMAIL_PW_RESET:
        context.update({"uid": "abc-def", "token": "abc-def"})
    elif email_type == EMAIL_VERIFICATION:
        context.update({"confirmation_url": "http://www.example.com/confirm/url"})
    elif email_type == EMAIL_RECEIPT:
        context.update(
            {
                "application": dict(
                    price=5000.0,
                    user=dict(
                        email="janedoe@example.com",
                        profile=dict(name="Jane Doe"),
                        legal_address=dict(
                            street_address=["795 Massachusetts Ave", "2nd Floor"],
                            city="Cambridge",
                            state_or_territory="US-MA",
                            country="US",
                            postal_code="02139",
                        ),
                    ),
                    bootcamp_run=dict(
                        title="Artificial Intelligence",
                        start_date=drf_datetime(now_in_utc() + timedelta(days=15)),
                        end_date=drf_datetime(now_in_utc() + timedelta(days=30)),
                    ),
                    orders=[
                        dict(
                            updated_on=drf_datetime(now_in_utc() - timedelta(days=21)),
                            total_price_paid=800.0,
                            payment_method="Credit Card",
                        ),
                        dict(
                            updated_on=drf_datetime(now_in_utc() - timedelta(days=14)),
                            total_price_paid=200.67,
                            payment_method="Wire Transfer",
                        ),
                        dict(
                            updated_on=drf_datetime(now_in_utc() - timedelta(days=7)),
                            total_price_paid=729.85,
                            payment_method="Credit Card",
                        ),
                    ],
                )
            }
        )

    return api.render_email_templates(email_type, context)


@method_decorator(csrf_exempt, name="dispatch")
class EmailDebuggerView(View):
    """Email debugger view"""

    form_cls = EmailDebuggerForm
    initial = {}
    template_name = "email_debugger.html"

    def get(self, request):
        """
        Dispalys the debugger UI
        """
        form = self.form_cls(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        Renders a test email
        """
        form = self.form_cls(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        subject, text_body, html_body = _render_email(form.cleaned_data["email_type"])

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "subject": subject,
                "html_body": html_body,
                "text_body": text_body,
            },
        )
