"""Management command to enroll users in a NovoEd course"""
from django.core.management.base import BaseCommand, CommandError

from klasses.models import BootcampRunEnrollment, BootcampRun
from profiles.api import fetch_user
from novoed.tasks import enroll_users_in_novoed_course


class Command(BaseCommand):
    """Management command to enroll users in a NovoEd course"""

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--run", type=str, help="The id or title of the bootcamp run", required=True
        )
        parser.add_argument(
            "--user",
            type=str,
            help="(Optional) The id, email, or username of the User",
            required=False,
        )

    def handle(self, *args, **options):
        run_property = options["run"]
        if run_property.isdigit():
            bootcamp_run = BootcampRun.objects.get(id=run_property)
        else:
            bootcamp_run = BootcampRun.objects.get(title=run_property)
        if bootcamp_run.novoed_course_stub is None:
            raise CommandError(
                f"Bootcamp run '{bootcamp_run.title}' does not have a novoed_course_stub value"
            )
        enrollment_filter = {"bootcamp_run": bootcamp_run}
        if options["user"]:
            user = fetch_user(options["user"])
            enrollment_filter = {"user": user}
        bootcamp_enrollment_qset = BootcampRunEnrollment.objects.filter(
            **enrollment_filter
        )
        if not bootcamp_enrollment_qset.exists():
            raise CommandError(
                f"No BootcampEnrollments found with the given filters: {enrollment_filter}"
            )

        self.stdout.write(
            "Enrolling {} user(s) in NovoEd course '{}'...".format(
                bootcamp_enrollment_qset.count(), bootcamp_run.novoed_course_stub
            )
        )
        user_ids = list(bootcamp_enrollment_qset.values_list("user_id", flat=True))
        task_result = enroll_users_in_novoed_course.apply(
            kwargs=dict(
                user_ids=user_ids, novoed_course_stub=bootcamp_run.novoed_course_stub
            )
        )
        self.stdout.write(str(task_result.result))
