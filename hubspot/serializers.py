"""
Serializers for hubspot
"""
import logging

from rest_framework import serializers

from profiles.models import Profile
from smapply.api import SMApplyTaskCache

log = logging.getLogger(__name__)

# Dictionary of demographics fields to sync with hubspot. Keys are the fields from the questionnaire.
# Values are the cleaned field name.
demo_sync_fields = {
    'Email Address': 'email',
    'First Name': 'first_name',
    'Last Name': 'last_name',
    'Once you heard about the program, what made you decide to apply?': 'why_apply',
    'Are you an MIT Bootcamp alumni?': 'alumni',
    'Industry': 'industry',
    'Nationality': 'nationality',
    'If you were referred by MIT Bootcamps alumni, please list their name(s) below:': 'referred_by',
    'Date of Birth': 'date_of_birth',
    'Work Experience': 'work_experience',
    'What other programs have you applied to?': 'other_programs',
    'Once your admission and participation is confirmed, your fellow Bootcampers '
    'will see the links you provided above.': 'agree_see_links',
    'Telephone Number': 'phone',
    'Job Title': 'jobtitle',
    'Media, Participant Release & License Release': 'participant_license_release',
    'MIT Bootcamps Honor Code\n(Select "I agree" to continue)': 'mit_honor_code',
    'Occupation': 'occupation',
    'Confidentiality and IP Rights': 'confidentiality',
    'Referral Information': 'referral_information',
    'How did you first hear about the Bootcamp?': 'hear_about_bootcamp',
    'Country/Region of Residence\n\n': 'country',
    'Gender': 'gender',
    'Company Name': 'company',
    'Highest Level of Education': 'highest_education',
    'Linkedin profile URL': 'linkedin_profile',
    'Liability Release & Waiver': 'liability_release',
}


class HubspotProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for outputting Profile objects in a suitable form for hubspot sync
    """
    def __init__(self, task_cache=None, **kwargs):
        if task_cache:
            self.task_cache = task_cache
        else:
            self.task_cache = SMApplyTaskCache()

        super().__init__(**kwargs)

    def get_demographics_data(self, instance):
        """
        Helper function to get demographics data from the Profile and format it for hubspot
        """
        # Use task cache to get task data by task_id
        task_definition = self.task_cache.get_task(instance.smapply_demographic_data.get('id'))
        responses = instance.smapply_demographic_data.get('data')

        # Iterate over demographics form fields to get response data from the Profile
        demographics_data = {}
        for field_name, mapping in demo_sync_fields.items():
            if field_name in task_definition:
                field_key = task_definition[field_name]['key']  # Unique lookup key for field
                if field_key not in responses:
                    continue
                if 'choices' in task_definition[field_name]:
                    # Lookup the response choice in the task definition dict of choices
                    response_id = responses[field_key]['response']
                    if response_id:
                        if isinstance(response_id, list):
                            # Some responses are lists but only allow a single answer.
                            # I think this has to do with the questions using checkboxes, not radio buttons.
                            response_id = response_id[0]
                        response = task_definition[field_name]['choices'][response_id]
                    else:  # Handle an empty list
                        response = ''
                else:
                    response = responses[field_key]['response']
                demographics_data[mapping] = response

        # If any fields aren't present then the associated program has a typo, or is otherwise missing data
        missing_fields = set(demo_sync_fields.values()) - set(demographics_data.keys())
        if missing_fields:
            log.error("Missing fields while syncing data for Profile with SMApply Id %s. Fields: %s",
                      instance.smapply_id, missing_fields)
        return demographics_data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.smapply_user_data:
            # Get user data, but overwrite it if demographics form exists
            data.update({
                'email': instance.smapply_user_data.get('email'),
                'first_name': instance.smapply_user_data.get('first_name'),
                'last_name': instance.smapply_user_data.get('last_name'),
            })
        if instance.smapply_demographic_data:
            data.update(self.get_demographics_data(instance))
        return data

    class Meta:
        model = Profile
        fields = ['smapply_id']
