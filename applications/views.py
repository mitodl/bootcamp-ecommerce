"""Views for bootcamp applications"""
from collections import OrderedDict

from django.db.models import Count, Subquery, OuterRef, IntegerField, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin

from applications.constants import SUBMISSION_STATUS_SUBMITTED, REVIEWABLE_APP_STATES
from applications.serializers import (
    BootcampApplicationDetailSerializer,
    BootcampApplicationSerializer,
    SubmissionReviewSerializer,
)
from applications.api import get_or_create_bootcamp_application
from applications.filters import ApplicationStepSubmissionFilterSet
from applications.models import (
    ApplicantLetter,
    ApplicationStepSubmission,
    BootcampApplication,
)
from ecommerce.models import Order
from klasses.models import BootcampRun, Bootcamp
from main.permissions import UserIsOwnerPermission, UserIsOwnerOrAdminPermission
from main.utils import serializer_date_format


class BootcampApplicationViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    View for fetching users' serialized bootcamp application(s)
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, UserIsOwnerOrAdminPermission)
    owner_field = "user"

    def get_queryset(self):
        if self.action == "retrieve":
            return BootcampApplication.objects.prefetch_state_data()
        else:
            return (
                BootcampApplication.objects.prefetch_related(
                    Prefetch(
                        "orders", queryset=Order.objects.filter(status=Order.FULFILLED)
                    )
                )
                .filter(user=self.request.user)
                .select_related("bootcamp_run__bootcamprunpage")
                .order_by("-created_on")
            )

    def get_serializer_context(self):
        added_context = {}
        if self.action == "list":
            added_context = {"include_page": True, "filtered_orders": True}
        return {**super().get_serializer_context(), **added_context}

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BootcampApplicationDetailSerializer
        elif self.action in {"list", "create"}:
            return BootcampApplicationSerializer
        raise MethodNotAllowed("Cannot perform the requested action.")

    def create(self, request, *args, **kwargs):
        bootcamp_run_id = request.data.get("bootcamp_run_id")
        if not bootcamp_run_id:
            raise ValidationError("Bootcamp run ID required.")
        if not BootcampRun.objects.filter(id=bootcamp_run_id).exists():
            return Response(
                data={"error": "Bootcamp does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        application, created = get_or_create_bootcamp_application(
            user=request.user, bootcamp_run_id=bootcamp_run_id
        )
        serializer_cls = self.get_serializer_class()
        return Response(
            data=serializer_cls(instance=application).data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK),
        )


class ReviewSubmissionPagination(LimitOffsetPagination):
    """Pagination class for ReviewSubmissionViewSet"""

    default_limit = 10
    max_limit = 1000
    facets = {}

    def paginate_queryset(self, queryset, request, view=None):
        """Paginate the queryset"""
        self.facets = self.get_facets(queryset)
        return super().paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        """Return a paginationed response, including facets"""
        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                    ("facets", self.facets),
                ]
            )
        )

    def get_facets(self, queryset):
        """Return a dictionary of facets"""
        statuses = (
            queryset.values("review_status")
            .annotate(count=Count("review_status"))
            .order_by("count")
        )
        qs = (
            queryset.values("bootcamp_application__bootcamp_run__bootcamp")
            .filter(bootcamp_application__bootcamp_run__bootcamp=OuterRef("pk"))
            .order_by()
            .annotate(count=Count("*"))
            .values("count")
        )
        bootcamps = (
            Bootcamp.objects.values("id", "title")
            .annotate(count=Subquery(qs, output_field=IntegerField()))
            .filter(count__gte=1)
            .distinct()
        )
        return {"review_statuses": statuses, "bootcamps": bootcamps}


class ReviewSubmissionViewSet(
    SerializerExtensionsAPIViewMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Admin view for managing application submissions
    """

    authentication_classes = (SessionAuthentication,)
    serializer_class = SubmissionReviewSerializer
    permission_classes = (IsAdminUser,)
    queryset = (
        ApplicationStepSubmission.objects.filter(
            Q(submission_status=SUBMISSION_STATUS_SUBMITTED)
            & Q(bootcamp_application__state__in=REVIEWABLE_APP_STATES)
        )
        .select_related(
            "bootcamp_application__user__profile",
            "bootcamp_application__user__legal_address",
        )
        .prefetch_related("content_object")
    )
    filterset_class = ApplicationStepSubmissionFilterSet
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = ReviewSubmissionPagination
    ordering_fields = ["created_on"]
    ordering = "created_on"


class UploadResumeView(GenericAPIView):
    """
    View for uploading resume and linkedin URL
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, UserIsOwnerPermission)
    lookup_field = "pk"
    owner_field = "user"
    queryset = BootcampApplication.objects.all()
    serializer_class = BootcampApplicationDetailSerializer

    def post(self, request, *args, **kwargs):
        """
        Update the application with resume and/or linkedin URL
        """
        application = self.get_object()
        linkedin_url = request.data.get("linkedin_url")
        resume_file = request.FILES.get("file")
        if linkedin_url is None and resume_file is None and not application.resume_file:
            raise ValidationError("At least one form of resume is required.")

        application.add_resume(resume_file=resume_file, linkedin_url=linkedin_url)
        # when state transition happens need to save manually
        application.save()

        return Response(
            {
                "resume_url": (
                    application.resume_file.url if application.resume_file else None
                ),
                "linkedin_url": application.linkedin_url,
                "resume_upload_date": serializer_date_format(
                    application.resume_upload_date
                ),
            },
            status=status.HTTP_200_OK,
        )


class LettersView(TemplateView):
    """
    Render a letter sent to an applicant
    """

    template_name = "letter_template_page.html"

    def get_context_data(self, **kwargs):
        """
        Fill in variables in the letter template
        """
        hash_code = kwargs.get("hash")
        letter = get_object_or_404(ApplicantLetter, hash=hash_code)
        return {"content": letter.letter_text}
