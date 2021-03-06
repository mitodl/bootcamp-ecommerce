"""Bootcamp application constants"""

from enum import Enum


SUBMISSION_VIDEO = "videointerviewsubmission"
SUBMISSION_QUIZ = "quizsubmission"
VALID_SUBMISSION_TYPE_CHOICES = [
    (SUBMISSION_VIDEO, "Video Interview"),
    (SUBMISSION_QUIZ, "Quiz"),
]
SUBMISSION_TYPE_STATE = {
    SUBMISSION_VIDEO: "AWAITING_VIDEO_INTERVIEW",
    SUBMISSION_QUIZ: "AWAITING_QUIZ_SUBMISSION",
}


class AppStates(Enum):
    """Enum of possible bootcamp application states"""

    AWAITING_PROFILE_COMPLETION = "AWAITING_PROFILE_COMPLETION"
    AWAITING_RESUME = "AWAITING_RESUME"
    AWAITING_USER_SUBMISSIONS = "AWAITING_USER_SUBMISSIONS"
    AWAITING_SUBMISSION_REVIEW = "AWAITING_SUBMISSION_REVIEW"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    COMPLETE = "COMPLETE"
    REJECTED = "REJECTED"
    REFUNDED = "REFUNDED"

    def __str__(self):
        """If an enum is silently cast to string it should be treated as if the user added .value to the end"""
        return str(self.value)


ORDERED_UNFINISHED_APP_STATES = [
    AppStates.AWAITING_PROFILE_COMPLETION.value,
    AppStates.AWAITING_RESUME.value,
    AppStates.AWAITING_USER_SUBMISSIONS.value,
    AppStates.AWAITING_SUBMISSION_REVIEW.value,
    AppStates.AWAITING_PAYMENT.value,
]
REVIEWABLE_APP_STATES = [
    AppStates.REJECTED.value,
    AppStates.AWAITING_PAYMENT.value,
    AppStates.AWAITING_SUBMISSION_REVIEW.value,
]
APPROVED_APP_STATES = [
    AppStates.AWAITING_PAYMENT.value,
    AppStates.COMPLETE.value,
    AppStates.REFUNDED.value,
]
REVIEW_COMPLETED_APP_STATES = APPROVED_APP_STATES + [AppStates.REJECTED.value]
VALID_APP_STATE_CHOICES = list(
    zip((member.value for member in AppStates), (member.value for member in AppStates))
)

REVIEW_STATUS_PENDING = "pending"
REVIEW_STATUS_APPROVED = "approved"
REVIEW_STATUS_REJECTED = "rejected"
REVIEW_STATUS_WAITLISTED = "waitlisted"
ALL_REVIEW_STATUSES = [
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_WAITLISTED,
]
VALID_REVIEW_STATUS_CHOICES = list(zip(ALL_REVIEW_STATUSES, ALL_REVIEW_STATUSES))
SUBMISSION_REVIEW_COMPLETED_STATES = {
    status for status in ALL_REVIEW_STATUSES if status != REVIEW_STATUS_PENDING
}

SUBMISSION_STATUS_PENDING = "pending"
SUBMISSION_STATUS_SUBMITTED = "submitted"
ALL_SUBMISSIONS_STATUSES = [SUBMISSION_STATUS_PENDING, SUBMISSION_STATUS_SUBMITTED]
VALID_SUBMISSION_STATUS_CHOICES = list(
    zip(ALL_SUBMISSIONS_STATUSES, ALL_SUBMISSIONS_STATUSES)
)

INTEGRATION_PREFIX = "BootcampApplication-"

LETTER_TYPE_APPROVED = "approved"
LETTER_TYPE_REJECTED = "rejected"
ALL_LETTER_TYPES = [LETTER_TYPE_APPROVED, LETTER_TYPE_REJECTED]
VALID_LETTER_TYPE_CHOICES = list(zip(ALL_LETTER_TYPES, ALL_LETTER_TYPES))
