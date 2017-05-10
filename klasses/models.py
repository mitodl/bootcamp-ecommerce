"""Models for klasses"""
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


class Bootcamp(models.Model):
    """
    A bootcamp
    """
    title = models.TextField()

    def __str__(self):
        return "Bootcamp {title}".format(title=self.title)


class Klass(models.Model):
    """
    A class within a bootcamp
    """
    bootcamp = models.ForeignKey(Bootcamp)
    title = models.TextField(blank=True)
    klass_key = models.IntegerField(unique=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

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
        - Start/end in same month: "May 5 - 10 2017"
        - Start/end in different months: "May 5 - June 10 2017"
        - Start/end in different years: "May 5 2017 - May 5 2018"
        - No end date: "May 5 2017"
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
                return '{} - {} {}'.format(start_date_month_day, formatted_end_date, self.end_date.year)
            else:
                return '{} {} - {} {}'.format(
                    start_date_month_day,
                    self.start_date.year,
                    end_date_month_day,
                    self.end_date.year
                )
        elif self.start_date:
            return '{} {}'.format(self.start_date.strftime(month_day_format), self.start_date.year)
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

    def __str__(self):
        return "Klass {title} of {bootcamp}".format(
            title=self.title,
            bootcamp=self.bootcamp,
        )


class Installment(models.Model):
    """
    A payment installment
    """
    klass = models.ForeignKey(Klass)
    installment_number = models.IntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    deadline = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('klass', 'installment_number')

    def __str__(self):
        return "Installment {installment_number} for {amount} for {klass}".format(
            installment_number=self.installment_number,
            amount=self.amount,
            klass=self.klass,
        )


class BootcampAdmissionCache(models.Model):
    """
    The cached data from the bootcamp admission
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    klass = models.ForeignKey(Klass)
    data = JSONField()

    class Meta:
        unique_together = (('user', 'klass'), )

    def __str__(self):
        """Object representation"""
        return 'Admission for user "{user}" in klass "{klass}"'.format(
            user=self.user.email,
            klass=self.klass.title
        )

    @classmethod
    def user_qset(cls, user):
        """
        Returns a queryset for the records associated with an User

        Args:
            user (User): an User object

        Returns:
            QuerySet: a queryset of all records for the provided user
        """
        return cls.objects.filter(user=user)

    @classmethod
    def delete_all_but(cls, user, klass_keys_list):
        """
        Given an user, deletes all her object in the cache but the provided klass keys

        Args:
            user (User): an User object
            course_ids_list (list): a list of course IDs to NOT be deleted

        Returns:
            None
        """
        cls.user_qset(user).exclude(klass__klass_key__in=klass_keys_list).delete()
