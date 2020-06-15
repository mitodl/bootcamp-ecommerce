"""views for jobma"""
import logging

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from applications.constants import (
    SUBMISSION_STATUS_PENDING,
    SUBMISSION_STATUS_SUBMITTED,
)
from applications.models import (
    ApplicationStepSubmission,
    ApplicationStep,
    BootcampApplication,
    BootcampRunApplicationStep,
    VideoInterviewSubmission,
)
from jobma.constants import JOBMA_COMPLETED_INTERVIEW_STATUSES
from jobma.models import Interview
from jobma.permissions import JobmaWebhookPermission


log = logging.getLogger(__name__)


class JobmaWebhookView(GenericAPIView):
    """An endpoint for Jobma to publish the interview status"""

    permission_classes = (JobmaWebhookPermission,)
    lookup_field = "pk"
    queryset = Interview.objects.all()

    def put(self, request, *args, **kwargs):
        """Update the Jobma interview status result"""
        status = request.data["status"]
        results_url = request.data.get("results_url")

        interview = self.get_object()
        interview.status = status
        interview.results_url = results_url
        interview.save_and_log(None)

        if status in JOBMA_COMPLETED_INTERVIEW_STATUSES:
            for (
                submission
            ) in interview.videointerviewsubmission.app_step_submissions.filter(
                submission_status=SUBMISSION_STATUS_PENDING
            ):
                submission.bootcamp_application.complete_interview()
                submission.bootcamp_application.save()

                submission.submission_status = SUBMISSION_STATUS_SUBMITTED
                submission.save()

        return Response(status=200)
