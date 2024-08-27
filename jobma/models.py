"""jobma models"""

from django.conf import settings
from django.db import models

from jobma.constants import JOBMA_INTERVIEW_STATUSES, PENDING
from klasses.models import BootcampRun
from main.models import AuditableModel, AuditModel
from main.utils import serialize_model_object


class Job(AuditableModel):
    """A job to be filled"""

    job_id = models.IntegerField()
    job_code = models.TextField()
    job_title = models.TextField()
    interview_template_id = models.IntegerField()
    run = models.OneToOneField(BootcampRun, on_delete=models.CASCADE)

    @classmethod
    def get_audit_class(cls):  # noqa: D102
        return JobAudit

    def to_dict(self):  # noqa: D102
        return serialize_model_object(self)

    def __str__(self):
        return f"Job {self.job_title}"


class JobAudit(AuditModel):
    """An audit model for Job"""

    job = models.ForeignKey(Job, null=True, on_delete=models.SET_NULL)

    @classmethod
    def get_related_field_name(cls):  # noqa: D102
        return "job"


class Interview(AuditableModel):
    """An interview for a job which has been created on Jobma"""

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    interview_url = models.TextField(blank=True, null=True)  # noqa: DJ001
    results_url = models.TextField(blank=True, null=True)  # noqa: DJ001
    status = models.TextField(
        default=PENDING,
        choices=[(status, status) for status in JOBMA_INTERVIEW_STATUSES],
    )
    interview_token = models.TextField(blank=True, null=True)  # noqa: DJ001

    @classmethod
    def get_audit_class(cls):  # noqa: D102
        return InterviewAudit

    def to_dict(self):  # noqa: D102
        return serialize_model_object(self)

    def __str__(self):
        return f"Interview for {self.job} by {self.applicant}"


class InterviewAudit(AuditModel):
    """Audit model for Interview"""

    interview = models.ForeignKey(Interview, null=True, on_delete=models.SET_NULL)

    @classmethod
    def get_related_field_name(cls):  # noqa: D102
        return "interview"
