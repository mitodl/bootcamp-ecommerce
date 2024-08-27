"""Abstract models for use in other applications"""

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import (
    SET_NULL,
    ForeignKey,
    JSONField,
    Model,
)
from mitol.common.models import TimestampedModel


class AuditModel(TimestampedModel):
    """An abstract base class for audit models"""

    acting_user = ForeignKey(User, null=True, on_delete=SET_NULL)
    data_before = JSONField(blank=True, null=True)
    data_after = JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_related_field_name(cls):
        """
        Returns:
            str: A field name which links the Auditable model to this model
        """
        raise NotImplementedError


class AuditableModel(Model):
    """An abstract base class for auditable models"""

    class Meta:
        abstract = True

    def to_dict(self):
        """
        Returns:
            dict:
                A serialized representation of the model object
        """
        raise NotImplementedError

    @classmethod
    def get_audit_class(cls):
        """
        Returns:
            class of Model:
                A class of a Django model used as the audit table
        """
        raise NotImplementedError

    @transaction.atomic
    def save_and_log(self, acting_user, *args, **kwargs):
        """
        Saves the object and creates an audit object.

        Args:
            acting_user (django.contrib.auth.models.User or None):
                The user who made the change to the model. May be None if inapplicable.
        """
        before_obj = self.__class__.objects.filter(id=self.id).first()
        self.save(*args, **kwargs)
        self.refresh_from_db()
        before_dict = None
        if before_obj is not None:
            before_dict = before_obj.to_dict()

        audit_kwargs = dict(  # noqa: C408
            acting_user=acting_user, data_before=before_dict, data_after=self.to_dict()
        )
        audit_class = self.get_audit_class()
        audit_kwargs[audit_class.get_related_field_name()] = self
        audit_class.objects.create(**audit_kwargs)


class ValidateOnSaveMixin(Model):
    """Mixin that calls field/model validation methods before saving a model object"""

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, **kwargs):  # noqa: D102, FBT002
        if not (force_insert or force_update):
            self.full_clean()
        super().save(force_insert=force_insert, force_update=force_update, **kwargs)
