"""Models for bootcamps"""
import datetime
import uuid
from functools import partial

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from main.models import TimestampedModel
from main.utils import now_in_utc, format_month_day
from klasses.constants import (
    ApplicationSource,
    INTEGRATION_PREFIX_PRODUCT,
    ENROLL_CHANGE_STATUS_CHOICES,
    DATE_RANGE_MONTH_FMT,
)


class ActiveCertificates(models.Manager):
    """
    Return the active certificates only
    """

    def get_queryset(self):
        """
        Returns:
            QuerySet: queryset for un-revoked certificates
        """
        return super().get_queryset().filter(is_revoked=False)


class Bootcamp(models.Model):
    """
    A bootcamp
    """

    title = models.TextField()
    legacy = models.BooleanField(default=False)

    def __str__(self):
        return "Bootcamp {title}".format(title=self.title)


class BootcampRun(models.Model):
    """
    A class within a bootcamp
    """

    bootcamp = models.ForeignKey(Bootcamp, on_delete=models.CASCADE)
    title = models.TextField(blank=True)
    source = models.CharField(
        null=True,
        blank=True,
        choices=[(source, source) for source in ApplicationSource.SOURCE_CHOICES],
        default=None,
        max_length=10,
    )
    run_key = models.IntegerField(unique=True, db_index=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    bootcamp_run_id = models.CharField(
        null=True, unique=True, blank=True, max_length=255
    )
    novoed_course_stub = models.CharField(null=True, blank=True, max_length=100)
    allows_skipped_steps = models.BooleanField(default=False)

    @property
    def page(self):
        """Gets the associated BootcampRunPage"""
        return getattr(self, "bootcamprunpage", None)

    @property
    def price(self):
        """
        Get price, the sum of all installments
        """
        return self.installment_set.aggregate(price=models.Sum("amount"))["price"]

    @property
    def formatted_date_range(self):
        """
        Returns a formatted date range.

        Example return values:
        - Start/end in same month: "May 5 - 10, 2017"
        - Start/end in different months: "May 5 - Sep 10, 2017"
        - Start/end in different years: "May 5, 2017 - May 5, 2018"
        - No end date: "May 5, 2017"
        """
        _format_month_day = partial(format_month_day, month_fmt=DATE_RANGE_MONTH_FMT)
        if self.start_date and self.end_date:
            start_month_day = _format_month_day(self.start_date)
            if self.start_date.year == self.end_date.year:
                if self.start_date.month == self.end_date.month:
                    formatted_end_date = self.end_date.day
                else:
                    formatted_end_date = _format_month_day(self.end_date)
                return "{} - {}, {}".format(
                    start_month_day, formatted_end_date, self.end_date.year
                )
            else:
                return "{}, {} - {}, {}".format(
                    start_month_day,
                    self.start_date.year,
                    _format_month_day(self.end_date),
                    self.end_date.year,
                )
        elif self.start_date:
            return "{}, {}".format(
                _format_month_day(self.start_date), self.start_date.year
            )
        else:
            return ""

    @property
    def display_title(self):
        """
        Returns a string that will be used to represent the bootcamp/run in the app
        """
        title_parts = [self.bootcamp.title]
        formatted_date_range = self.formatted_date_range
        if formatted_date_range:
            title_parts.append(formatted_date_range)
        return ", ".join(title_parts)

    @property
    def payment_deadline(self):
        """
        Get the overall payment deadline
        """
        return self.installment_set.aggregate(payment_deadline=models.Max("deadline"))[
            "payment_deadline"
        ]

    @property
    def next_installment(self):
        """
        Get the next installment
        """
        return self.installment_set.filter(
            deadline__gte=datetime.datetime.now(tz=pytz.UTC)
        ).first()

    @property
    def next_payment_deadline_days(self):
        """
        Returns the number of days until the next payment is due
        """
        next_installment = self.next_installment
        if next_installment is None:
            return
        due_in = next_installment.deadline - datetime.datetime.now(tz=pytz.UTC)
        return due_in.days

    @property
    def total_due_by_next_deadline(self):
        """
        Returns the total amount due by the next deadline
        """
        next_installment = self.next_installment
        if next_installment is None:
            return self.price
        return self.installment_set.filter(
            deadline__lte=next_installment.deadline
        ).aggregate(price=models.Sum("amount"))["price"]

    @property
    def integration_id(self):
        """
        Return an integration id to be used by Hubspot as the unique product id.
        This is necessary because the integration id used to be based on Bootcamp.id,
        and is now based on BootcampRun (formerly Klass).  This requires that there be no
        overlap in integration ids between new and old products.

        Returns:
            str: the integration id
        """
        return f"{INTEGRATION_PREFIX_PRODUCT}{self.id}"

    @property
    def is_payable(self):
        """
        Returns True if the start date is set and is in the future

        Returns:
            bool: True if the start date is set and is in the future
        """
        # NOTE: We have an Installment model with a 'deadline' property. Those installments are meant to
        # specify increments when a user should pay for the bootcamp run. Practically, those deadlines are just
        # "suggestions". For now, we're making a conscious decision to prevent a user from making payments based on
        # the bootcamp run start date rather than the last installment deadline date.
        return self.start_date is not None and now_in_utc() < self.start_date

    def personal_price(self, user):
        """
        Returns the personal price (if any) or standard price for a bootcamp run

        Args:
            user(User): the user to get a price for

        Returns:
            Decimal: the price for the bootcamp run
        """
        personal_price = self.personal_prices.filter(user=user).first()
        if personal_price is not None:
            return personal_price.price
        return self.price

    def __str__(self):
        return self.display_title


class Installment(models.Model):
    """
    A payment installment
    """

    bootcamp_run = models.ForeignKey(BootcampRun, on_delete=models.CASCADE)
    deadline = models.DateTimeField(null=False)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        index_together = ["bootcamp_run", "deadline"]
        unique_together = ("bootcamp_run", "deadline")
        ordering = ["bootcamp_run", "deadline"]

    def __str__(self):
        return (
            "Installment for '{bootcamp_run}'; ${amount}; deadline {deadline}".format(
                bootcamp_run=self.bootcamp_run.title,
                amount=self.amount,
                deadline=self.deadline.strftime("%b %d %Y"),
            )
        )


class PersonalPrice(models.Model):
    """Personal price for a bootcamp run"""

    bootcamp_run = models.ForeignKey(
        BootcampRun, on_delete=models.CASCADE, related_name="personal_prices"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="run_prices")
    price = models.DecimalField(max_digits=20, decimal_places=2)
    application_stage = models.TextField(blank=True)

    class Meta:
        unique_together = ("bootcamp_run", "user")

    def __str__(self):
        return f"user='{self.user.email}', run='{self.bootcamp_run.title}', price={self.price}"


class BootcampRunEnrollment(TimestampedModel):
    """An enrollment in a bootcamp run by a user"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    bootcamp_run = models.ForeignKey(
        BootcampRun, on_delete=models.CASCADE, related_name="enrollments"
    )
    change_status = models.CharField(
        choices=ENROLL_CHANGE_STATUS_CHOICES, max_length=20, null=True, blank=True
    )
    novoed_sync_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(
        default=True,
        help_text="Indicates whether or not this enrollment should be considered active",
    )
    user_certificate_is_blocked = models.BooleanField(
        default=False,
        help_text="Indicates whether or not this user enrollment will get certificate.",
    )

    class Meta:
        unique_together = ("user", "bootcamp_run")

    def __str__(self):
        return f"Enrollment for {self.bootcamp_run}"


class BaseCertificate(models.Model):
    """
    Common properties for certificate models
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_revoked = models.BooleanField(
        default=False,
        help_text="Indicates whether or not the certificate is revoked",
        verbose_name="revoked",
    )

    class Meta:
        abstract = True

    def revoke(self):
        """Revokes certificate"""
        self.is_revoked = True
        self.save()
        return self

    def unrevoke(self):
        """Unrevokes certificate"""
        self.is_revoked = False
        self.save()
        return self

    def get_certified_object_id(self):
        """Gets the id of the certificate's bootcamp program/run"""
        raise NotImplementedError


class BootcampRunCertificate(TimestampedModel, BaseCertificate):
    """
    Model for storing bootcamp run certificates
    """

    bootcamp_run = models.ForeignKey(
        BootcampRun, null=False, on_delete=models.CASCADE, related_name="certificates"
    )

    objects = ActiveCertificates()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("user", "bootcamp_run")

    def get_certified_object_id(self):
        return self.bootcamp_run_id

    @property
    def link(self):
        """
        Get the link at which this certificate will be served
        Format: /certificate/<uuid>/
        Example: /certificate/93ebd74e-5f88-4b47-bb09-30a6d575328f/
        """
        return "/certificate/{}/".format(str(self.uuid))

    @property
    def start_end_dates(self):
        """Returns the start and end date for bootcamp object duration"""
        return self.bootcamp_run.start_date, self.bootcamp_run.end_date

    def __str__(self):
        return "BootcampRunCertificate for user={user}, run={bootcamp_run} ({uuid})".format(
            user=self.user.username, bootcamp_run=self.bootcamp_run.id, uuid=self.uuid
        )
