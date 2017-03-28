"""Models for klasses"""
from django.db import models


class Bootcamp(models.Model):
    """
    A bootcamp
    """
    title = models.TextField()


class Klass(models.Model):
    """
    A class within a bootcamp
    """
    bootcamp = models.ForeignKey(Bootcamp)
    title = models.TextField(blank=True)
    klass_id = models.IntegerField()
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)


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
