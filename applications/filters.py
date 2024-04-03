"""Applications filters"""

from django_filters import FilterSet, NumberFilter

from applications.models import ApplicationStepSubmission


class ApplicationStepSubmissionFilterSet(FilterSet):
    """FilterSet for ApplicationStepSubmission"""

    bootcamp_run_id = NumberFilter(
        field_name="bootcamp_application__bootcamp_run__id", lookup_expr="exact"
    )

    class Meta:
        model = ApplicationStepSubmission
        fields = {"review_status": ["exact", "in"]}
