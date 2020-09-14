"""NovoEd async tasks"""
import logging

from django.contrib.auth import get_user_model

from main.celery import app
from novoed import api

log = logging.getLogger(__name__)
User = get_user_model()


@app.task
def enroll_users_in_novoed_course(*, user_ids, novoed_course_stub):
    """
    Enrolls a group of users in a NovoEd course

    Returns:
        dict: A dict containing information about the number of users created, the number that already existed,
            and the number that failed
    """
    users = User.objects.select_related("profile", "legal_address").filter(
        id__in=user_ids
    )
    results = {"created": 0, "existed": 0, "failed": 0}
    for user in users:
        try:
            created, existed = api.enroll_in_novoed_course(user, novoed_course_stub)
            if created:
                results["created"] += 1
            elif existed:
                results["existed"] += 1
        except:  # pylint: disable=bare-except
            results["failed"] += 1
            log.exception(
                "User enrollment in NovoEd failed (%s, %s)",
                user.email,
                novoed_course_stub,
            )
    return results


@app.task
def unenroll_user_from_novoed_course(*, user_id, novoed_course_stub):
    """
    Unenrolls a user from a NovoEd course

    Returns:
        (string, bool): The user's email paired with a flag indicating whether or not the unenrollment succeeded
    """
    user = User.objects.select_related("profile", "legal_address").get(id=user_id)
    try:
        api.unenroll_from_novoed_course(user, novoed_course_stub)
        return user.email, True
    except:  # pylint: disable=bare-except
        log.exception(
            "User unenrollment from NovoEd failed (%s, %s)",
            user.email,
            novoed_course_stub,
        )
        return user.email, False
