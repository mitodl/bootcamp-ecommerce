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
export const ALERT_TYPE_UNUSED_COUPON = "unused-coupon"
export const ALTER_TYPE_B2B_ORDER_STATUS = "b2b-order-status"

// HTML title for different pages
export const LOGIN_EMAIL_PAGE_TITLE = "Sign In"
export const LOGIN_PASSWORD_PAGE_TITLE = LOGIN_EMAIL_PAGE_TITLE

export const FORGOT_PASSWORD_PAGE_TITLE = "Forgot Password"
export const FORGOT_PASSWORD_CONFIRM_PAGE_TITLE = FORGOT_PASSWORD_PAGE_TITLE

export const EDIT_PROFILE_PAGE_TITLE = "Edit Profile"
export const VIEW_PROFILE_PAGE_TITLE = "View Profile"

export const REGISTER_EMAIL_PAGE_TITLE = "Register"
export const REGISTER_CONFIRM_PAGE_TITLE = REGISTER_EMAIL_PAGE_TITLE
export const REGISTER_DETAILS_PAGE_TITLE = REGISTER_EMAIL_PAGE_TITLE
export const REGISTER_EXTRA_DETAILS_PAGE_TITLE = REGISTER_EMAIL_PAGE_TITLE

export const REGISTER_ERROR_PAGE_TITLE = "Registration Error"
export const REGISTER_DENIED_PAGE_TITLE = REGISTER_ERROR_PAGE_TITLE

export const ACCOUNT_SETTINGS_PAGE_TITLE = "Account Settings"
export const EMAIL_CONFIRM_PAGE_TITLE = "Confirm Email Change"

export const RECEIPT_PAGE_TITLE = "Receipt"
