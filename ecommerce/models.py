"""Models for ecommerce"""
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db.models import (
    CharField,
    DecimalField,
    ForeignKey,
    SET_NULL,
    TextField,
)


from bootcamp.models import (
    AuditableModel,
    AuditModel,
    TimestampedModel,
)
from bootcamp.utils import serialize_model_object


class Order(AuditableModel, TimestampedModel):
    """
    Represents a payment the user has made
    """
    FULFILLED = 'fulfilled'
    FAILED = 'failed'
    CREATED = 'created'
    REFUNDED = 'refunded'

    STATUSES = [CREATED, FULFILLED, FAILED, REFUNDED]

    user = ForeignKey(settings.AUTH_USER_MODEL)
    status = CharField(
        choices=[(status, status) for status in STATUSES],
        default=CREATED,
        max_length=30,
    )

    total_price_paid = DecimalField(decimal_places=2, max_digits=20)

    def __str__(self):
        """Description for Order"""
        return "Order {}, status={} for user={}".format(self.id, self.status, self.user)

    @classmethod
    def get_audit_class(cls):
        return OrderAudit

    def to_dict(self):
        """
        Add any Lines to the serialized representation of the Order
        """
        data = serialize_model_object(self)
        data['lines'] = [serialize_model_object(line) for line in self.line_set.all()]
        return data


class OrderAudit(AuditModel):
    """
    Audit model for Order. This also stores information for Line.
    """
    order = ForeignKey(Order, null=True, on_delete=SET_NULL)

    @classmethod
    def get_related_field_name(cls):
        return 'order'

    def __str__(self):
        """Description for Order"""
        return "Order {}".format(self.id)


class Line(TimestampedModel):
    """
    Represents a line item in the order
    """
    order = ForeignKey(Order)
    klasse_id = TextField()
    price = DecimalField(decimal_places=2, max_digits=20)
    description = TextField()

    def __str__(self):
        """Description for Line"""
        return "Line for {order}, price={price}, klasse_id={klasse_id}, description={description}".format(
            order=self.order,
            price=self.price,
            klasse_id=self.klasse_id,
            description=self.description,
        )


class Receipt(TimestampedModel):
    """
    The contents of the message from CyberSource about an Order fulfillment or cancellation
    """
    order = ForeignKey(Order, null=True)
    data = JSONField()

    def __str__(self):
        """Description of Receipt"""
        if self.order:
            return "Receipt for order {}".format(self.order.id)
        else:
            return "Receipt with no attached order"
