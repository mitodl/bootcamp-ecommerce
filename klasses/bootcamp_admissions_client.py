"""
APIs to access the remote bootcamp app that controls the admissions
"""
from klasses.models import Bootcamp


class BootcampAdmissionClient:
    """
    Client for the bootcamp admission portal
    """

    admissions = []
    payable_klasses = {}
    payable_klasses_ids = []

    def __init__(self, user_email):
        self.user_email = user_email
        # this call should be somehow fault tolerant
        self.admissions = self._get_admissions()
        self.payable_klasses = self._get_payable_klasses()
        self.payable_klasses_ids = list(self.payable_klasses.keys())

    def _get_admissions(self):
        """
        Requests the bootcamp klasses where the user has been admitted.

        For now it just returns the first of the klasses in the local database for all the users.
        Eventually this should make requests to the remote app and be fault tolerant
        """
        # this is the expected structure according to
        # https://github.com/mitodl/bootcamp-ecommerce/issues/15
        return {
            "user": self.user_email,
            "bootcamps": [
                {
                    "bootcamp_id": None,  # NOTE:this is the ID on the remote web service (we do not need it)
                    "bootcamp_title": bootcamp.title,
                    "klasses":  [
                        {
                            "klass_id": klass.klass_id,  # NOTE: this is the ID on the remote web service
                            "klass_name": klass.title,
                            "is_user_eligible_to_pay": True
                        } for klass in bootcamp.klass_set.order_by('id')
                    ]
                } for bootcamp in Bootcamp.objects.all().order_by('id')
            ]
        }

    def _get_payable_klasses(self):
        """
        Returns a list of the payable klasses.
        """
        adm_klasses = {}
        for bootcamp in self.admissions.get("bootcamps", []):
            for klass in bootcamp.get("klasses", []):
                if klass.get("is_user_eligible_to_pay") is True:
                    adm_klasses[klass["klass_id"]] = klass
        return adm_klasses

    def can_pay_klass(self, klass_id):
        """
        Whether the user can pay for a specific klass
        """
        return klass_id in self.payable_klasses_ids
