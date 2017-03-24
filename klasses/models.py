"""Models for klasses"""
from django.db.models.base import Model
from django.db.models.fields import (
    DateTimeField,
    DecimalField,
    TextField,
    IntegerField,
)
from django.db.models.fields.related import ForeignKey


class Bootcamp(Model):
    """
    A bootcamp
    """
    title = TextField()


class Klass(Model):
    """
    A class within a bootcamp
    """
    bootcamp = ForeignKey(Bootcamp)
    klass_id = IntegerField()
    price = DecimalField(max_digits=20, decimal_places=2)


class Installment(Model):
    """
    A payment installment
    """
    klass = ForeignKey(Klass)
    installment_number = IntegerField()
    min_amount = DecimalField(max_digits=20, decimal_places=2)
    deadline = DateTimeField(null=True)

    class Meta:
        unique_together = ('klass', 'installment_number')
