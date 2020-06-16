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

    def __str__(self):
        """If an enum is silently cast to string it should be treated as if the user added .value to the end"""
        return self.value


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
