// Put constants here
export const ORDER_FULFILLED = "fulfilled"
export const TOAST_SUCCESS = "done"
export const TOAST_FAILURE = "error"

export const GENDER_CHOICES = [
  ["m", "Male"],
  ["f", "Female"],
  ["o", "Other/Prefer Not to Say"]
]

export const EMPLOYMENT_INDUSTRY = [
  "Association, Nonprofit Organization, NGO",
  "Business and Professional Services",
  "Construction and Engineering",
  "Education",
  "Energy",
  "Financials",
  "Government / Armed Forces",
  "Food, Beverages and Tobacco",
  "Government",
  "Health Care",
  "Industrials",
  "Retailing",
  "Materials",
  "Media",
  "Information technology",
  "Transportation",
  "Other",
  "Prefer not to say"
]

export const EMPLOYMENT_EXPERIENCE = [
  [2, "Less than 2 years"],
  [5, "2-5 years"],
  [10, "6 - 10 years"],
  [15, "11 - 15 years"],
  [20, "16 - 20 years"],
  [21, "More than 20 years"],
  [0, "Prefer not to say"]
]

export const EMPLOYMENT_SIZE = [
  [1, "Small/Start-up (1+ employees)"],
  [9, "Small/Home office (1-9 employees)"],
  [99, "Small (10-99 employees)"],
  [999, "Small to medium-sized (100-999 employees)"],
  [9999, "Medium-sized (1000-9999 employees)"],
  [10000, "Large Enterprise (10,000+ employees)"],
  [0, "Other (N/A or Don't know)"]
]

export const EMPLOYMENT_FUNCTION = [
  "Accounting",
  "Administrative",
  "Arts and Design",
  "Business Development/Sales",
  "Community & Social Services",
  "Consulting",
  "Education",
  "Engineering",
  "Entrepreneurship",
  "Finance",
  "Healthcare Services",
  "Human Resources",
  "Information Technology",
  "Legal",
  "Media/Communications/Marketing",
  "Military & Protective Services",
  "Operations",
  "Program & Product Management",
  "Purchasing",
  "Quality Assurance",
  "Real Estate",
  "Research",
  "Support",
  "Other"
]

export const HIGHEST_EDUCATION_CHOICES = [
  "Doctorate",
  "Master's or professional degree",
  "Bachelor's degree",
  "Associate degree",
  "Secondary/high school",
  "Junior secondary/junior high/middle school",
  "Elementary/primary school",
  "No formal education",
  "Other education"
]

export const ADDRESS_LINES_MAX = 4
export const US_ALPHA_2 = "US"
export const CA_ALPHA_2 = "CA"

export const US_POSTAL_CODE_REGEX = /[0-9]{5}(-[0-9]{4}){0,1}/
export const CA_POSTAL_CODE_REGEX = /[A-Z][0-9][A-Z] [0-9][A-Z][0-9]/
export const COUNTRIES_REQUIRING_POSTAL_CODE = [US_ALPHA_2, CA_ALPHA_2]
export const COUNTRIES_REQUIRING_STATE = [US_ALPHA_2, CA_ALPHA_2]

export const ALERT_TYPE_TEXT = "text"

export const APP_STATE_IN_PROGRESS = "In Progress"
export const APP_STATE_IN_REVIEW = "In Review"
export const APP_STATE_COMPLETE = "Complete"
export const APP_STATE_REJECTED = "Rejected"

export const APP_STATE_TEXT_MAP = {
  AWAITING_PROFILE_COMPLETION: APP_STATE_IN_PROGRESS,
  AWAITING_RESUME:             APP_STATE_IN_PROGRESS,
  AWAITING_USER_SUBMISSIONS:   APP_STATE_IN_PROGRESS,
  AWAITING_SUBMISSION_REVIEW:  APP_STATE_IN_REVIEW,
  AWAITING_PAYMENT:            APP_STATE_IN_PROGRESS,
  COMPLETE:                    APP_STATE_COMPLETE,
  REJECTED:                    APP_STATE_REJECTED
}

export const SUBMISSION_VIDEO = "videointerviewsubmission"
export const SUBMISSION_QUIZ = "quizsubmission"

export const REVIEW_STATUS_APPROVED = "approved"
export const REVIEW_STATUS_REJECTED = "rejected"
export const REVIEW_STATUS_PENDING = "pending"
export const REVIEW_STATUS_WAITLISTED = "waitlisted"

export const REVIEW_STATUS_DISPLAY_MAP = {
  [REVIEW_STATUS_APPROVED]:   ["Approved", "text-primary"],
  [REVIEW_STATUS_REJECTED]:   ["Rejected", "text-warning"],
  [REVIEW_STATUS_PENDING]:    ["Not Reviewed", "text-secondary"],
  [REVIEW_STATUS_WAITLISTED]: ["Waitlisted", "text-secondary"]
}

export const REVIEW_STATUS_TEXT_MAP = {
  [REVIEW_STATUS_APPROVED]:   REVIEW_STATUS_APPROVED,
  [REVIEW_STATUS_REJECTED]:   REVIEW_STATUS_REJECTED,
  [REVIEW_STATUS_PENDING]:    REVIEW_STATUS_PENDING,
  [REVIEW_STATUS_WAITLISTED]: REVIEW_STATUS_WAITLISTED
}

export const SUBMISSION_STATUS_PENDING = "pending"
export const SUBMISSION_STATUS_SUBMITTED = "submitted"

export const SUBMISSION_STATUS_TEXT_MAP = {
  SUBMISSION_STATUS_PENDING:   SUBMISSION_STATUS_PENDING,
  SUBMISSION_STATUS_SUBMITTED: SUBMISSION_STATUS_SUBMITTED
}

// HTML title for different pages
export const LOGIN_EMAIL_PAGE_TITLE = "Sign In"
export const LOGIN_PASSWORD_PAGE_TITLE = LOGIN_EMAIL_PAGE_TITLE

export const FORGOT_PASSWORD_PAGE_TITLE = "Forgot Password"
export const FORGOT_PASSWORD_CONFIRM_PAGE_TITLE = FORGOT_PASSWORD_PAGE_TITLE

export const EDIT_PROFILE_PAGE_TITLE = "Edit Profile"
export const VIEW_PROFILE_PAGE_TITLE = "View Profile"

export const REGISTER_EMAIL_PAGE_TITLE = "Register"
export const REGISTER_CONFIRM_PAGE_TITLE = REGISTER_EMAIL_PAGE_TITLE
export const REGISTER_DETAILS_PAGE_TITLE = "Create Profile"
export const REGISTER_EXTRA_DETAILS_PAGE_TITLE = REGISTER_DETAILS_PAGE_TITLE

export const REGISTER_ERROR_PAGE_TITLE = "Registration Error"
export const REGISTER_DENIED_PAGE_TITLE = REGISTER_ERROR_PAGE_TITLE

export const ACCOUNT_SETTINGS_PAGE_TITLE = "Account Settings"
export const EMAIL_CONFIRM_PAGE_TITLE = "Confirm Email Change"

export const RECEIPT_PAGE_TITLE = "Receipt"

export const APPLICATIONS_DASHBOARD_PAGE_TITLE = "Dashboard"
export const REVIEW_DETAIL_TITLE = "Admission"

export const CMS_SITE_WIDE_NOTIFICATION = "cms-site-wide-notification"
export const CMS_NOTIFICATION_SELECTOR = ".site-wide"
export const CMS_NOTIFICATION_ID_ATTR = "data-notification-id"
export const CMS_NOTIFICATION_LCL_STORAGE_ID = "dismissedNotification"

// Drawer content types
export const PROFILE_VIEW = "profileView"
export const PROFILE_EDIT = "profileEdit"
export const PAYMENT = "payment"
export const NEW_APPLICATION = "newApplication"
export const TAKE_VIDEO_INTERVIEW = "TAKE_VIDEO_INTERVIEW"
export const RESUME_UPLOAD = "resumeUpload"

export const JOBMA = "Jobma"
export const JOBMA_SITE = "jobma.com"

export const ALLOWED_FILE_EXTENSIONS = {
  pdf: "application/pdf"
}

// Submission facets
export const STATUS_FACET_KEY = "review_statuses"
export const BOOTCAMP_FACET_KEY = "bootcamps"

export const FACET_DISPLAY_NAMES = {
  [STATUS_FACET_KEY]:   "Application Status",
  [BOOTCAMP_FACET_KEY]: "Bootcamp"
}

export const FACET_OPTION_LABEL_KEYS = {
  [STATUS_FACET_KEY]:   "review_status",
  [BOOTCAMP_FACET_KEY]: "title"
}

export const FACET_ORDER = [BOOTCAMP_FACET_KEY, STATUS_FACET_KEY]
