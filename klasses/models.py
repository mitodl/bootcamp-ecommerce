"""Models for klasses"""
import datetime

import pytz
from django.contrib.auth.models import User
from django.db import models

from klasses.constants import ApplicationSource


class Bootcamp(models.Model):
    """
    A bootcamp
    """
    title = models.TextField()
    legacy = models.BooleanField(default=False)

    def __str__(self):
        return "Bootcamp {title}".format(title=self.title)


class Klass(models.Model):
    """
    A class within a bootcamp
    """
    bootcamp = models.ForeignKey(Bootcamp)
    title = models.TextField(blank=True)
    source = models.CharField(
        null=False,
        choices=[(status, status) for status in ApplicationSource.SOURCE_CHOICES],
        default=ApplicationSource.FLUIDREVIEW,
        max_length=10,
    )
    klass_key = models.IntegerField()
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('klass_key', 'source')

    @property
    def price(self):
        """
        Get price, the sum of all installments
        """
        return self.installment_set.aggregate(price=models.Sum('amount'))['price']

    @property
    def formatted_date_range(self):
        """
        Returns a formatted date range.

        Example return values:
        - Start/end in same month: "May 5 - 10, 2017"
        - Start/end in different months: "May 5 - June 10, 2017"
        - Start/end in different years: "May 5, 2017 - May 5, 2018"
        - No end date: "May 5, 2017"
        """
        month_day_format = '%b %-d'
        if self.start_date and self.end_date:
            start_date_month_day = self.start_date.strftime(month_day_format)
            end_date_month_day = self.end_date.strftime(month_day_format)
            if self.start_date.year == self.end_date.year:
                if self.start_date.month == self.end_date.month:
                    formatted_end_date = self.end_date.day
                else:
                    formatted_end_date = end_date_month_day
                return '{} - {}, {}'.format(start_date_month_day, formatted_end_date, self.end_date.year)
            else:
                return '{}, {} - {}, {}'.format(
                    start_date_month_day,
                    self.start_date.year,
                    end_date_month_day,
                    self.end_date.year
                )
        elif self.start_date:
            return '{}, {}'.format(self.start_date.strftime(month_day_format), self.start_date.year)
        else:
            return ''

    @property
    def display_title(self):
        """
        Returns a string that will be used to represent the bootcamp/klass in the app
        """
        title_parts = [self.bootcamp.title]
        formatted_date_range = self.formatted_date_range
        if formatted_date_range:
            title_parts.append(formatted_date_range)
        return ', '.join(title_parts)

    @property
    def payment_deadline(self):
        """
        Get the overall payment deadline
        """
        return self.installment_set.aggregate(payment_deadline=models.Max('deadline'))['payment_deadline']

    @property
    def next_installment(self):
        """
        Get the next installment
        """
        return self.installment_set.filter(deadline__gte=datetime.datetime.now(tz=pytz.UTC)).first()

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
            deadline__lte=next_installment.deadline).aggregate(price=models.Sum('amount'))['price']

    def personal_price(self, user):
        """
        Returns the personal price (if any) or standard price for a klass

        Args:
            user(User): the user to get a price for

        Returns:
            Decimal: the price for the klass
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
    klass = models.ForeignKey(Klass)
    deadline = models.DateTimeField(null=False)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        index_together = ['klass', 'deadline']
        unique_together = ('klass', 'deadline')
        ordering = ['klass', 'deadline', ]

    def __str__(self):
        return "Installment for '{klass}'; ${amount}; deadline {deadline}".format(
            klass=self.klass.title,
            amount=self.amount,
            deadline=self.deadline.strftime('%b %d %Y')
        )


class PersonalPrice(models.Model):
    """Personal price for a klass"""
    klass = models.ForeignKey(
        Klass,
        on_delete=models.CASCADE,
        related_name='personal_prices'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='klass_prices'
    )
    price = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        unique_together = ('klass', 'user')
