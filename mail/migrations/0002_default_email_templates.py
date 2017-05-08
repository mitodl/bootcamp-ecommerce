from django.db import migrations, models


def forwards_func(apps, schema_editor):
    """
    It adds default email templates
    """
    AutomaticReminderEmail = apps.get_model("mail", "AutomaticReminderEmail")
    db_alias = schema_editor.connection.alias

    # first email for reminders to pay one week before deadline
    AutomaticReminderEmail.objects.using(db_alias).create(
        days_before=7,
        email_subject="Payment due for %recipient.bootcamp_name% Bootcamp",
        email_body="""Dear %recipient.full_name%,

Your tuition payment for %recipient.bootcamp_name% Bootcamp is due. \
Your remaining balance is $%recipient.remaining_balance%. \
Please pay your balance before %recipient.payment_due_date%.

You can pay online with a credit card or PayPal at %recipient.site_URL%.

If you have submitted the payment by wire transfer, could you please send us the transaction receipt? \
We will need this to confirm receipt of funds through the wire department.


Thanks & best regards,

Admissions Committee
MIT Global Entrepreneurship Bootcamps
        """
    )

    # second email for reminders to pay 2 days before deadline
    AutomaticReminderEmail.objects.using(db_alias).create(
        days_before=2,
        email_subject="%recipient.bootcamp_name% Bootcamp Payment due in 2 days",
        email_body="""Dear %recipient.full_name%,

Your tuition payment for %recipient.bootcamp_name% Bootcamp is due in two days. \
Your remaining balance is $%recipient.remaining_balance%. \
Please pay your balance before %recipient.payment_due_date%.

You can pay online with a credit card or PayPal at %recipient.site_URL%.

If you have submitted the payment by wire transfer, could you please send us the transaction receipt? \
We will need this to confirm receipt of funds through the wire department.


Thanks & best regards,

Admissions Committee
MIT Global Entrepreneurship Bootcamps
        """
    )

    # third email for reminders to pay on the day of deadline
    AutomaticReminderEmail.objects.using(db_alias).create(
        days_before=0,
        email_subject="%recipient.bootcamp_name% Bootcamp Payment due NOW",
        email_body="""Dear %recipient.full_name%,

Your tuition payment for %recipient.bootcamp_name% Bootcamp is due today. \
Your remaining balance is $%recipient.remaining_balance%. \
Please pay your balance before %recipient.payment_due_date%.

You can pay online with a credit card or PayPal at %recipient.site_URL%.

If you have submitted the payment by wire transfer, could you please send us the transaction receipt? \
We will need this to confirm receipt of funds through the wire department.


Thanks & best regards,

Admissions Committee
MIT Global Entrepreneurship Bootcamps
        """
    )


def reverse_func(apps, schema_editor):
    """
    It deletes all the default email templates
    """
    AutomaticReminderEmail = apps.get_model("mail", "AutomaticReminderEmail")
    db_alias = schema_editor.connection.alias
    AutomaticReminderEmail.objects.using(db_alias).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
