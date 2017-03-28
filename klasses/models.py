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
    klass_id = models.IntegerField()
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

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
    min_amount = models.DecimalField(max_digits=20, decimal_places=2)
    deadline = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('klass', 'installment_number')

    def __str__(self):
        return "Installment {installment_number} for {min_amount} for {klass}".format(
            installment_number=self.installment_number,
            min_amount=self.min_amount,
            klass=self.klass,
        )
