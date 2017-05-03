"""Models for klasses"""
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
