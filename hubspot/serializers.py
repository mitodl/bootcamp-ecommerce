"""
Serializers for hubspot
"""
import logging
from decimal import Decimal

from rest_framework import serializers

from ecommerce.models import Order
from klasses.models import Bootcamp, PersonalPrice
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


class HubspotContactSerializer(serializers.ModelSerializer):
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
                    if response_id is not None and response_id != []:
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


class HubspotProductSerializer(serializers.ModelSerializer):
    """
    Serializer for turning a Bootcamp into a hubspot Product
    """
    class Meta:
        model = Bootcamp
        fields = ['title']


class HubspotDealSerializer(serializers.ModelSerializer):
    """
    Serializer for turning a PersonalPrice into a hubspot deal
    """
    name = serializers.SerializerMethodField()
    purchaser = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    bootcamp_name = serializers.SerializerMethodField()

    def get_name(self, instance):
        """Get a formatted name for the deal"""
        return f"Bootcamp-application-{instance.id}"

    def get_purchaser(self, instance):
        """Get the id of the associated user"""
        from hubspot.api import format_hubspot_id
        return format_hubspot_id(instance.user.profile.id)

    def get_price(self, instance):
        """Get a string of the price"""
        return instance.price.to_eng_string()

    def get_bootcamp_name(self, instance):
        """Get a string of the price"""
        return instance.klass.bootcamp.title

    def to_representation(self, instance):
        # Populate order data
        data = super().to_representation(instance)

        orders = Order.objects.filter(user=instance.user, line__klass_key=instance.klass.klass_key)
        if orders.exists():
            amount_paid = Decimal(0)
            for order in orders:
                if order.status == Order.FULFILLED:
                    amount_paid += order.total_price_paid

            data['total_price_paid'] = amount_paid.to_eng_string()
            if amount_paid >= instance.price:
                data['status'] = 'shipped'
            elif amount_paid > 0:
                data['status'] = 'processed'
            else:
                data['status'] = 'checkout_completed'
        else:
            data['status'] = 'checkout_pending'

        return data

    class Meta:
        model = PersonalPrice
        fields = ['name', 'application_stage', 'price', 'purchaser', 'bootcamp_name']


class HubspotLineSerializer(serializers.ModelSerializer):
    """
    Serializer for turning a PersonalPrice into a hubspot line item
    """
    order = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    def get_order(self, instance):
        """Get the id of the associated deal"""
        from hubspot.api import format_hubspot_id
        return format_hubspot_id(instance.id)

    def get_product(self, instance):
        """Get the id of the associated Bootcamp"""
        from hubspot.api import format_hubspot_id
        return format_hubspot_id(instance.klass.bootcamp.id)

    class Meta:
        model = PersonalPrice
        fields = ['order', 'product']
