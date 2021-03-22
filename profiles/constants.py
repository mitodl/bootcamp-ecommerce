"""User constants"""
import pycountry


USERNAME_MAX_LEN = 30


# Defined in edX Profile model
MALE = "m"
FEMALE = "f"
OTHER = "o"
GENDER_CHOICES = (
    (MALE, "Male"),
    (FEMALE, "Female"),
    (OTHER, "Other/Prefer Not to Say"),
)

COMPANY_SIZE_CHOICES = (
    (None, "----"),
    (1, "Small/Start-up (1+ employees)"),
    (9, "Small/Home office (1-9 employees)"),
    (99, "Small (10-99 employees)"),
    (999, "Small to medium-sized (100-999 employees)"),
    (9999, "Medium-sized (1000-9999 employees)"),
    (10000, "Large Enterprise (10,000+ employees)"),
    (0, "Other (N/A or Don't know)"),
)

YRS_EXPERIENCE_CHOICES = (
    (None, "----"),
    (2, "Less than 2 years"),
    (5, "2-5 years"),
    (10, "6 - 10 years"),
    (15, "11 - 15 years"),
    (20, "16 - 20 years"),
    (21, "More than 20 years"),
    (0, "Prefer not to say"),
)

HIGHEST_EDUCATION_CHOICES = (
    (None, "----"),
    ("Doctorate", "Doctorate"),
    ("Master's or professional degree", "Master's or professional degree"),
    ("Bachelor's degree", "Bachelor's degree"),
    ("Associate degree", "Associate degree"),
    ("Secondary/high school", "Secondary/high school"),
    (
        "Junior secondary/junior high/middle school",
        "Junior secondary/junior high/middle school",
    ),
    ("Elementary/primary school", "Elementary/primary school"),
    ("No formal education", "No formal education"),
    ("Other education", "Other education"),
)

COUNTRIES_REQUIRING_POSTAL_CODE = (
    pycountry.countries.get(alpha_2="US"),
    pycountry.countries.get(alpha_2="CA"),
)

ALUM_LEARNER_EMAIL = "Learner Email"
ALUM_BOOTCAMP_NAME = "Bootcamp Name"
ALUM_BOOTCAMP_RUN_TITLE = "Bootcamp Run Title"
ALUM_BOOTCAMP_START_DATE = "Bootcamp Start Date"
ALUM_BOOTCAMP_END_DATE = "Bootcamp End Date"
ALUM_HEADER_FIELDS = [
    ALUM_LEARNER_EMAIL,
    ALUM_BOOTCAMP_NAME,
    ALUM_BOOTCAMP_RUN_TITLE,
    ALUM_BOOTCAMP_START_DATE,
    ALUM_BOOTCAMP_END_DATE,
]
