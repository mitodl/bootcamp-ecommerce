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

from ecommerce.constants import CARD_TYPES
from main.models import AuditableModel, AuditModel, TimestampedModel
from main.utils import serialize_model_object
from klasses.models import BootcampRun


class Order(AuditableModel, TimestampedModel):
    """
    Represents a payment the user has made
    """

    FULFILLED = "fulfilled"
    FAILED = "failed"
    CREATED = "created"
    REFUNDED = "refunded"

    STATUSES = [CREATED, FULFILLED, FAILED, REFUNDED]

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    status = CharField(
        choices=[(status, status) for status in STATUSES],
        default=CREATED,
        max_length=30,
    )
    total_price_paid = DecimalField(decimal_places=2, max_digits=20)
    application = ForeignKey(
        "applications.BootcampApplication",
        on_delete=CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name="orders",
    )

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
    def run_title(self):
        """Display title of the bootcamp run that was purchased in this Order"""
        bootcamp_run = self.get_bootcamp_run()
        if not bootcamp_run:
            return ""
        return bootcamp_run.display_title

    @classmethod
    def get_audit_class(cls):
        return OrderAudit

    def to_dict(self):
        """
        Add any Lines to the serialized representation of the Order
        """
        data = serialize_model_object(self)
        data["lines"] = [serialize_model_object(line) for line in self.line_set.all()]
        return data

    def get_bootcamp_run(self):
        """
        Fetches the bootcamp run that was purchased in this Order

        Returns:
            BootcampRun: The bootcamp run that was purchased in this order.
        """
        line = self.line_set.first()
        if not line:
            return None
        return line.bootcamp_run


class OrderAudit(AuditModel):
    """
    Audit model for Order. This also stores information for Line.
    """

    order = ForeignKey(Order, null=True, on_delete=SET_NULL)

    @classmethod
    def get_related_field_name(cls):
        return "order"

    def __str__(self):
        """Description for Order"""
        return "Order {}".format(self.id)


class Line(TimestampedModel):
    """
    Represents a line item in the order
    """

    order = ForeignKey(Order, on_delete=CASCADE)
    run_key = IntegerField()
    bootcamp_run = ForeignKey(BootcampRun, null=True, on_delete=SET_NULL)
    price = DecimalField(decimal_places=2, max_digits=20)
    description = TextField()

    def __str__(self):
        """Description for Line"""
        return "Line for {order}, price={price}, bootcamp_run_id={bootcamp_run_id}, description={description}".format(
            order=self.order,
            price=self.price,
            bootcamp_run_id=self.bootcamp_run_id,
            description=self.description,
        )

    @classmethod
    def fulfilled_for_user(cls, user):
        """
        Returns the list of lines for fulfilled orders for a specific user
        """
        return cls.objects.filter(order__user=user, order__status=Order.FULFILLED)

    @classmethod
    def for_user_bootcamp_run(cls, user, bootcamp_run):
        """
        Returns all the orders that are associated to the payment of a specific run_key
        """
        return (
            cls.fulfilled_for_user(user)
            .filter(bootcamp_run=bootcamp_run)
            .order_by("order__created_on")
        )

    @classmethod
    def total_paid_for_bootcamp_run(cls, user, bootcamp_run):
        """
        Returns the total amount paid for a bootcamp run
        """
        return cls.for_user_bootcamp_run(user, bootcamp_run).aggregate(
            total=Sum("price")
        )


class Receipt(TimestampedModel):
    """
    The contents of the message from CyberSource about an Order fulfillment or cancellation
    """

    order = ForeignKey(Order, null=True, on_delete=CASCADE)
    data = JSONField()

    @property
    def payment_method(self):
        """Try to guess the payment source based on the Cybersource receipt"""
        payment_method = self.data.get("req_payment_method")
        if payment_method == "card":
            card_type = self.data.get("req_card_type")
            card_type_description = CARD_TYPES.get(card_type, "")
            card_number = self.data.get("req_card_number", "")

            return f"{card_type_description} | {card_number}"
        elif payment_method == "paypal":
            return "PayPal"

    def __str__(self):
        """Description of Receipt"""
        if self.order:
            return "Receipt for order {}".format(self.order.id)
        else:
            return "Receipt with no attached order"
