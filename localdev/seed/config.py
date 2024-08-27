"""Data seeding configuration/constants"""

import os
from enum import Enum

from django.conf import settings

from klasses.models import Bootcamp, BootcampRun

SEED_DATA_PREFIX = "Seed "
SEED_DATA_FILE_DIR_PATH = os.path.join(settings.BASE_DIR, "localdev/seed/resources/")  # noqa: PTH118
SEED_DATA_FILE_NAME = "seed_data.json"
SEED_DATA_FILE_PATH = os.path.join(SEED_DATA_FILE_DIR_PATH, SEED_DATA_FILE_NAME)  # noqa: PTH118
# This dict indicates which field for each model should be used to
# (a) find an existing object for some data we're deserializing, and
# (b) prepend a string indicating that the object is seed data.
SEED_DATA_KEY_FIELDS = {Bootcamp: "title", BootcampRun: "title"}


class DateRangeOption(Enum):
    """Options for date ranges"""

    future = "future"
    current = "current"
    past = "past"
