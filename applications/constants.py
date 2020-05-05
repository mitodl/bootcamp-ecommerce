"""Bootcamp application constants"""

from enum import Enum


class SubmissionTypes(Enum):
    """Enum of possible bootcamp application submission types"""
    VIDEO_INTERVIEW = "video_interview"
    QUIZ = "quiz"


VALID_SUBMISSION_TYPE_CHOICES = list(zip(
    (member.value for member in SubmissionTypes),
    (member.value for member in SubmissionTypes),
))


class AppStates(Enum):
    """Enum of possible bootcamp application states"""
    AWAITING_PROFILE_COMPLETION = "AWAITING_PROFILE_COMPLETION"
    AWAITING_RESUME = "AWAITING_RESUME"
    AWAITING_USER_SUBMISSIONS = "AWAITING_USER_SUBMISSIONS"
    AWAITING_SUBMISSION_REVIEW = "AWAITING_SUBMISSION_REVIEW"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    COMPLETE = "COMPLETE"
    REJECTED = "REJECTED"


VALID_APP_STATE_CHOICES = list(zip(
    (member.value for member in AppStates),
    (member.value for member in AppStates),
))
REVIEW_STATUS_APPROVED = "approved"
REVIEW_STATUS_REJECTED = "rejected"
REVIEW_STATUS_WAITING = "waiting"
ALL_REVIEW_STATUSES = [REVIEW_STATUS_APPROVED, REVIEW_STATUS_REJECTED, REVIEW_STATUS_WAITING]
VALID_REVIEW_STATUS_CHOICES = list(zip(ALL_REVIEW_STATUSES, ALL_REVIEW_STATUSES))
