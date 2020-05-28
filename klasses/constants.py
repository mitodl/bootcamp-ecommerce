"""Klasses constants"""


class ApplicationSource:
    """Simple class for possible WebHookRequest parsing statuses"""

    SMAPPLY = "SMApply"
    FLUIDREVIEW = "FluidRev"

    SOURCE_CHOICES = [None, SMAPPLY, FLUIDREVIEW]
