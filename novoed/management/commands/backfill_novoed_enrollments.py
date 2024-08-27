"""Management command to enroll users in a NovoEd course"""

from django.core.management.base import BaseCommand, CommandError

from klasses.api import fetch_bootcamp_run
from klasses.models import BootcampRunEnrollment
from novoed.tasks import enroll_users_in_novoed_course
from profiles.api import fetch_user


class Command(BaseCommand):
    """Management command to enroll users in a NovoEd course"""

    help = __doc__

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--run",
            type=str,
            help="The id, title, or display title of the bootcamp run",
            required=True,
        )
        parser.add_argument(
            "--user",
            type=str,
            help="(Optional) The id, email, or username of the User",
            required=False,
        )

    def handle(self, *args, **options):  # noqa: ARG002, D102
        bootcamp_run = fetch_bootcamp_run(options["run"])
        if bootcamp_run.novoed_course_stub is None:
            raise CommandError(
                f"Bootcamp run '{bootcamp_run.title}' does not have a novoed_course_stub value"  # noqa: EM102
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
                f"No BootcampEnrollments found with the given filters: {enrollment_filter}"  # noqa: EM102
            )

        self.stdout.write(
            "Enrolling {} user(s) in NovoEd course '{}'...".format(
                bootcamp_enrollment_qset.count(), bootcamp_run.novoed_course_stub
            )
        )
        user_ids = list(bootcamp_enrollment_qset.values_list("user_id", flat=True))
        task_result = enroll_users_in_novoed_course.apply(
            kwargs=dict(  # noqa: C408
                user_ids=user_ids, novoed_course_stub=bootcamp_run.novoed_course_stub
            )
        )
        self.stdout.write(str(task_result.result))
