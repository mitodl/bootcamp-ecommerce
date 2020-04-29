"""Models for ecommerce"""
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db.models import (
    CharField,
    CASCADE,
    DecimalField,
    ForeignKey,
    IntegerField,
    SET_NULL,
    TextField,
    Sum,
)


from main.models import (
    AuditableModel,
    AuditModel,
    TimestampedModel,
)
from main.utils import serialize_model_object
from klasses.models import Klass


class Order(AuditableModel, TimestampedModel):
    """
    Represents a payment the user has made
    """
    FULFILLED = 'fulfilled'
    FAILED = 'failed'
    CREATED = 'created'
    REFUNDED = 'refunded'

    STATUSES = [CREATED, FULFILLED, FAILED, REFUNDED]

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    status = CharField(
        choices=[(status, status) for status in STATUSES],
        default=CREATED,
        max_length=30,
    )

    total_price_paid = DecimalField(decimal_places=2, max_digits=20)

    def __str__(self):
        """Description for Order"""
        return "Order {}, status={} for user={}".format(self.id, self.status, self.user)

    @property
    def line_description(self):
        """Description of the first line in the Order (usually there should be only one)"""
        line = self.line_set.first()
        if not line:
            return ""
        return line.description

    @property
    def klass_title(self):
        """Title of the klass being paid for"""
        klass = self.get_klass()
        if not klass:
            return ""
        return klass.title

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

    def get_klass(self):
        """
        klass being paid for

        Returns:
            Klass: klass that order is for.

        """
        line = self.line_set.first()
        if not line:
            return None
        return Klass.objects.filter(klass_key=line.klass_key).first()


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
    order = ForeignKey(Order, on_delete=CASCADE)
    klass_key = IntegerField()
    price = DecimalField(decimal_places=2, max_digits=20)
    description = TextField()

    def __str__(self):
        """Description for Line"""
        return "Line for {order}, price={price}, klass_key={klass_key}, description={description}".format(
            order=self.order,
            price=self.price,
            klass_key=self.klass_key,
            description=self.description,
        )

    @classmethod
    def fulfilled_for_user(cls, user):
        """
        Returns the list of lines for fulfilled orders for a specific user
        """
        return cls.objects.filter(order__user=user, order__status=Order.FULFILLED).order_by('klass_key')

    @classmethod
    def for_user_klass(cls, user, klass_key):
        """
        Returns all the orders that are associated to the payment of a specific klass_key
        """
        return cls.fulfilled_for_user(user).filter(klass_key=klass_key).order_by('order__created_on')

    @classmethod
    def total_paid_for_klass(cls, user, klass_key):
        """
        Returns the total amount paid for a klass
        """
        return cls.for_user_klass(user, klass_key).aggregate(total=Sum('price'))


class Receipt(TimestampedModel):
    """
    The contents of the message from CyberSource about an Order fulfillment or cancellation
    """
    order = ForeignKey(Order, null=True, on_delete=CASCADE)
    data = JSONField()

    def __str__(self):
        """Description of Receipt"""
        if self.order:
            return "Receipt for order {}".format(self.order.id)
        else:
            return "Receipt with no attached order"
