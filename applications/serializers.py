"""Serializers for bootcamp applications"""
from rest_framework import serializers

from applications import models
from applications.constants import AppStates, REVIEW_STATUS_APPROVED
from applications.exceptions import InvalidApplicationStateException
from ecommerce.serializers import ApplicationOrderSerializer
from klasses.serializers import BootcampRunSerializer
from main.utils import get_filename_from_path, now_in_utc
from profiles.serializers import UserSerializer


class BootcampRunStepSerializer(serializers.ModelSerializer):
    """BootcampRunApplicationStep serializer"""

    step_order = serializers.SerializerMethodField()
    submission_type = serializers.SerializerMethodField()

    def get_step_order(self, bootcamp_run_step):
        """Returns the step order of the application step"""
        return bootcamp_run_step.application_step.step_order

    def get_submission_type(self, bootcamp_run_step):
        """Returns the submission type of the application step"""
        return bootcamp_run_step.application_step.submission_type

    class Meta:
        model = models.BootcampRunApplicationStep
        fields = ["id", "due_date", "step_order", "submission_type"]


class SubmissionSerializer(serializers.ModelSerializer):
    """ApplicationStepSubmission serializer"""

    class Meta:
        model = models.ApplicationStepSubmission
        fields = [
            "id",
            "run_application_step_id",
            "submitted_date",
            "review_status",
            "review_status_date",
        ]
        read_only_fields = ("submitted_date", "review_status", "review_status_date")


class BootcampApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed BootcampApplication serializer"""

    resume_filename = serializers.SerializerMethodField()
    payment_deadline = serializers.SerializerMethodField()
    run_application_steps = serializers.SerializerMethodField()
    submissions = SubmissionSerializer(many=True, read_only=True)
    orders = ApplicationOrderSerializer(many=True, read_only=True)
    bootcamp_run = BootcampRunSerializer(read_only=True)

    def get_resume_filename(self, bootcamp_application):
        """Gets the resume filename (without the path) if one exists"""
        return (
            None
            if not bootcamp_application.resume_file
            else get_filename_from_path(bootcamp_application.resume_file.name)
        )

    def get_payment_deadline(self, bootcamp_application):
        """Gets the deadline date of the last installment for the given bootcamp run"""
        payment_deadline = bootcamp_application.bootcamp_run.payment_deadline
        return serializers.DateTimeField().to_representation(payment_deadline)

    def get_run_application_steps(self, bootcamp_application):
        """Gets serialized bootcamp run application steps"""
        return BootcampRunStepSerializer(
            instance=bootcamp_application.bootcamp_run.application_steps.all(),
            many=True,
        ).data

    class Meta:
        model = models.BootcampApplication
        fields = [
            "id",
            "bootcamp_run",
            "state",
            "resume_filename",
            "linkedin_url",
            "resume_upload_date",
            "created_on",
            "payment_deadline",
            "run_application_steps",
            "submissions",
            "orders",
        ]


class BootcampApplicationSerializer(serializers.ModelSerializer):
    """BootcampApplication serializer"""

    bootcamp_run = BootcampRunSerializer()

    class Meta:
        model = models.BootcampApplication
        fields = ["id", "state", "created_on", "bootcamp_run"]


class SubmissionReviewSerializer(SubmissionSerializer):
    """ApplicationStepSubmission serializer for reviewers"""

    bootcamp_application = BootcampApplicationSerializer(required=False, read_only=True)
    learner = UserSerializer(
        source="bootcamp_application.user", required=False, read_only=True
    )

    def validate(self, attrs):
        """Validate incoming data for a write"""
        bootcamp_application = self.instance.bootcamp_application

        if "review_status" in attrs:
            if bootcamp_application.state != AppStates.AWAITING_SUBMISSION_REVIEW.value:
                # HTTP 409 error
                raise InvalidApplicationStateException(
                    detail="The BootcampApplication is not awaiting submission review (id: {}, state: {})".format(
                        bootcamp_application.id, bootcamp_application.state
                    )
                )
            attrs["review_status_date"] = now_in_utc()

        return attrs

    def update(self, instance, validated_data):
        """Update an ApplicationStepSubmission"""
        instance = super().update(instance, validated_data)

        if "review_status" in validated_data:
            bootcamp_application = instance.bootcamp_application
            if instance.review_status == REVIEW_STATUS_APPROVED:
                bootcamp_application.approve_submission()
            else:
                bootcamp_application.reject_submission()
            bootcamp_application.save()

        return instance

    class Meta(SubmissionSerializer.Meta):
        fields = SubmissionSerializer.Meta.fields + ["bootcamp_application", "learner"]
        read_only_fields = ("submitted_date", "review_status_date")
