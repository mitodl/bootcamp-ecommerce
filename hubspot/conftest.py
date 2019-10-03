"""
Fixtures for hubspot tests
"""
import copy
from datetime import datetime
from types import SimpleNamespace

import pytz
from django.conf import settings
import pytest
from hubspot.api import hubspot_timestamp

TIMESTAMPS = [
    datetime(2017, 1, 1, tzinfo=pytz.utc),
    datetime(2017, 1, 2, tzinfo=pytz.utc),
    datetime(2017, 1, 3, tzinfo=pytz.utc),
    datetime(2017, 1, 4, tzinfo=pytz.utc),
    datetime(2017, 1, 5, tzinfo=pytz.utc),
    datetime(2017, 1, 6, tzinfo=pytz.utc),
    datetime(2017, 1, 7, tzinfo=pytz.utc),
    datetime(2017, 1, 8, tzinfo=pytz.utc),
]

FAKE_OBJECT_ID = 1234


error_response_json = [
    {
        "portalId": 5_890_463,
        "objectType": "CONTACT",
        "integratorObjectId": f"{settings.HUBSPOT_ID_PREFIX}-16",
        "changeOccurredTimestamp": hubspot_timestamp(TIMESTAMPS[0]),
        "errorTimestamp": hubspot_timestamp(TIMESTAMPS[7]),
        "type": "UNKNOWNERROR",
        "details": 'Error performing[CREATE] CONTACT[16] for portal 5890463, error was [5890463] create/update '
                   'by email failed - java.util.concurrent.CompletionException: com.hubspot.properties.exceptions.'
                   'InvalidProperty: {"validationResults":[{"isValid":false,"message":"2019-05-13T12:05:53.602759Z '
                   'was not a valid long.","error":"INVALIDLONG","name":"createdate"}],"status":"error","message":'
                   '"Property values were not valid","correlationId":"fcde9e27-6e3b-4b3b-83c2-f6bd01289685",'
                   '"requestId":"8ede7b56-8269-4a5c-b2ea-a48a2dd9cd5d',
        "status": "OPEN",
    },
    {
        "portalId": 5_890_463,
        "objectType": "CONTACT",
        "integratorObjectId": f"{settings.HUBSPOT_ID_PREFIX}-55",
        "changeOccurredTimestamp": hubspot_timestamp(TIMESTAMPS[0]),
        "errorTimestamp": hubspot_timestamp(TIMESTAMPS[5]),
        "type": "UNKNOWNERROR",
        "details": 'Error performing[CREATE] CONTACT[55] for portal 5890463, error was [5890463] create/update '
                   'by email failed - java.util.concurrent.CompletionException: com.hubspot.properties.exceptions.'
                   'InvalidProperty: {"validationResults":[{"isValid":false,"message":"2019-05-21T17:32:43.135139Z '
                   'was not a valid long.","error":"INVALIDLONG","name":"createdate"}],"status":"error","message":'
                   '"Property values were not valid","correlationId":"51274e2f-d839-4476-a077-eba7a38d3786",'
                   '"requestId":"9c1f2ded-78da-41a2-a607-568acfbd908f',
        "status": "OPEN",
    },
    {
        "portalId": 5_890_463,
        "objectType": "DEAL",
        "integratorObjectId": f"{settings.HUBSPOT_ID_PREFIX}-116",
        "changeOccurredTimestamp": hubspot_timestamp(TIMESTAMPS[0]),
        "errorTimestamp": hubspot_timestamp(TIMESTAMPS[4]),
        "type": "UNKNOWNERROR",
        "details": 'Error performing[CREATE] DEAL[116] for portal 5890463, error was [5890463] create/update by '
                   'email failed - java.util.concurrent.CompletionException: com.hubspot.properties.exceptions.'
                   'InvalidProperty: {"validationResults":[{"isValid":false,"message":"2019-05-13T12:05:53.602759Z '
                   'was not a valid long.","error":"INVALIDLONG","name":"createdate"}],"status":"error","message":'
                   '"Property values were not valid","correlationId":"fcde9e27-6e3b-4b3b-83c2-f6bd01289685",'
                   '"requestId":"8ede7b56-8269-4a5c-b2ea-a48a2dd9cd5d',
        "status": "OPEN",
    },
    {
        "portalId": 5_890_463,
        "objectType": "DEAL",
        "integratorObjectId": f"{settings.HUBSPOT_ID_PREFIX}-155",
        "changeOccurredTimestamp": hubspot_timestamp(TIMESTAMPS[0]),
        "errorTimestamp": hubspot_timestamp(TIMESTAMPS[3]),
        "type": "UNKNOWNERROR",
        "details": 'Error performing[CREATE] DEAL[155] for portal 5890463, error was [5890463] create/update by '
                   'email failed - java.util.concurrent.CompletionException: com.hubspot.properties.exceptions.'
                   'InvalidProperty: {"validationResults":[{"isValid":false,"message":"2019-05-21T17:32:43.135139Z '
                   'was not a valid long.","error":"INVALIDLONG","name":"createdate"}],"status":"error","message":'
                   '"Property values were not valid","correlationId":"51274e2f-d839-4476-a077-eba7a38d3786",'
                   '"requestId":"9c1f2ded-78da-41a2-a607-568acfbd908f',
        "status": "OPEN",
    },
]

smapply_demographic_data = {
    'completed_at': '2019-09-23T15:06:26',
    'created_at': '2019-09-23T15:00:39',
    'data': {
        '1VTOWzfalA': {'label': 'Email Address', 'response': 'test_user@test.co'},
        '1iyRtJNtoX': {'label': 'Last Name', 'response': 'LastName'},
        '1skbq4pS1K': {'label': 'Show us your initiative and commitment', 'response': '1/1/2025'},
        '3qP7UE82Bh': {'label': 'Once you heard about the program, what made you decide ...',
                       'response': 'Some kind of answer'},
        '3rwUmuAZuF': {'label': 'Are you an MIT Bootcamp alumni?', 'response': 1},
        '8JgmHI7gTA': {'label': 'Industry', 'response': 6},
        '9sH6VF8bTE': {'label': 'Nationality', 'response': 183},
        'BiPgp5nz8r': {'label': 'If you were referred by MIT Bootcamps alumni, please li...', 'response': 'A person'},
        'BzgWgZZxIk': {'label': 'Date of Birth', 'response': '1/1/1991'},
        'ELiFgQuQCM': {'label': 'Work Experience', 'response': 4},
        'J1aVhQhx2c': {'label': 'First Name', 'response': 'FirstName'},
        'NSDGkHd4MW': {'label': 'What other programs have you applied to?', 'response': 'None okay'},
        'Npbm9TdTEl': {'label': 'Once your admission and participation is confirmed, you...', 'response': 1},
        'RMXABSNMVw': {'label': 'Telephone Number', 'response': '1234567890'},
        'TVOKbPLpT1': {'label': 'Job Title', 'response': 'Fake Job'},
        'WtfFURdRVs': {'label': 'Media, Participant Release & License Release', 'response': [0]},
        'aTM1RzDhWC': {'label': 'MIT Bootcamps Honor Code\n(Select "I agree" to continue)', 'response': [0]},
        'b1w3k41sEJ': {'label': 'Occupation', 'response': 6},
        'dTBBKNMkVp': {'label': 'Confidentiality and IP Rights', 'response': [0]},
        'eHs8rzdmhW': {'label': 'Referral Information', 'response': 'some kind of response'},
        'iAiXHo9ctv': {'label': 'How did you first hear about the Bootcamp?', 'response': 8},
        'mKB692vrUs': {'label': 'Country/Region of Residence\n\n', 'response': 183},
        'nM7vW8Laa4': {'label': 'Gender', 'response': 0},
        'vHpRHIw9Xk': {'label': 'Company Name', 'response': 'Fake Name'},
        'vnPTughA3S': {'label': 'Highest Level of Education', 'response': 8},
        'xT6TFzHruM': {'label': 'Linkedin profile URL', 'response': 'https://www.linkedin.com'},
        'xubvuT7xTq': {'label': 'Signature',
                       'response': 'assets/survey-uploads/123/456/signature.svg'},
        'y47FmfSdAl': {'label': 'Liability Release & Waiver', 'response': [0]}
    },
    'id': 677172,
    'name': 'Part 1: Complete Your Application Form',
    'stage': {'id': 311343, 'title': 'Round 1 - Application Stage'},
    'status': 3,
    'type': 1,
    'updated_at': '2019-09-23T15:06:27'
}

smapply_task_data = {
    'created_at': '2019-09-09T08:46:41', 'deadline': None, 'edit_after_complete': True, 'edit_after_deadline': False,
    'fields': {
        '1VTOWzfalA': {'identifier': None, 'name': 'Email Address'},
        '1iyRtJNtoX': {'identifier': None, 'name': 'Last Name'},
        '1skbq4pS1K': {'identifier': None, 'name': 'Show us your initiative and commitment'},
        '3qP7UE82Bh': {'identifier': None, 'name': 'Once you heard about the program, what made you decide to apply?'},
        '3rwUmuAZuF': {'choices': [{'index': 0, 'label': 'Yes', 'score': 1}, {'index': 1, 'label': 'No', 'score': 2}],
                       'identifier': None, 'name': 'Are you an MIT Bootcamp alumni?', 'other': False},
        '8JgmHI7gTA': {'choices': [{'index': 4, 'label': 'Apparel & Fashion', 'score': 5},
                                   {'index': 5, 'label': 'Architecture & Planning', 'score': 6},
                                   {'index': 6, 'label': 'Arts and Crafts', 'score': 7}],
                       'identifier': None, 'name': 'Industry', 'other': False},
        '9sH6VF8bTE': {'choices': [{'index': 181, 'label': 'United Arab Emirates', 'score': 182},
                                   {'index': 182, 'label': 'United Kingdom', 'score': 183},
                                   {'index': 183, 'label': 'United States', 'score': 184}],
                       'identifier': None, 'name': 'Nationality', 'other': False},
        'BiPgp5nz8r': {'identifier': None,
                       'name': 'If you were referred by MIT Bootcamps alumni, please list their name(s) below:'},
        'BzgWgZZxIk': {'identifier': None, 'name': 'Date of Birth'},
        'ELiFgQuQCM': {'choices': [{'index': 0, 'label': 'Less than a year', 'score': 1},
                                   {'index': 1, 'label': '1-2 years', 'score': 2},
                                   {'index': 2, 'label': '3-5 years', 'score': 3},
                                   {'index': 3, 'label': '5-10 years', 'score': 4},
                                   {'index': 4, 'label': '10 years or more', 'score': 5}],
                       'identifier': None, 'name': 'Work Experience', 'other': False},
        'J1aVhQhx2c': {'identifier': None, 'name': 'First Name'},
        'NSDGkHd4MW': {'identifier': None, 'name': 'What other programs have you applied to?'},
        'Npbm9TdTEl': {'choices': [{'index': 0, 'label': 'I Agree', 'score': 1},
                                   {'index': 1, 'label': 'I Disagree', 'score': 2}],
                       'identifier': None,
                       'name': 'Once your admission and participation is confirmed, '
                               'your fellow Bootcampers will see the links you provided above.',
                       'other': False},
        'RMXABSNMVw': {'identifier': None, 'name': 'Telephone Number'},
        'TVOKbPLpT1': {'identifier': None, 'name': 'Job Title'},
        'WtfFURdRVs': {'choices': [{'index': 0, 'label': 'I Agree', 'score': 1}],
                       'identifier': None, 'name': 'Media, Participant Release & License Release', 'other': False},
        'aTM1RzDhWC': {'choices': [{'index': 0, 'label': 'I Agree', 'score': 1}],
                       'identifier': None, 'name': 'MIT Bootcamps Honor Code\n(Select "I agree" to continue)',
                       'other': False},
        'b1w3k41sEJ': {'choices': [{'index': 0, 'label': 'Employed Full-Time', 'score': 1},
                                   {'index': 1, 'label': 'Employed Part-Time', 'score': 2},
                                   {'index': 2, 'label': 'Self-employed', 'score': 3},
                                   {'index': 3, 'label': 'Not employed, but looking for work', 'score': 4},
                                   {'index': 4, 'label': 'Not employed and not looking for work', 'score': 5},
                                   {'index': 5, 'label': 'Homemaker', 'score': 6},
                                   {'index': 6, 'label': 'Retired', 'score': 7},
                                   {'index': 7, 'label': 'Student', 'score': 8},
                                   {'index': 8, 'label': 'Prefer Not to Answer', 'score': 9}],
                       'identifier': None, 'name': 'Occupation', 'other': False},
        'dTBBKNMkVp': {'choices': [{'index': 0, 'label': 'I Agree', 'score': 1}],
                       'identifier': None, 'name': 'Confidentiality and IP Rights', 'other': False},
        'eHs8rzdmhW': {'identifier': None, 'name': 'Referral Information'},
        'iAiXHo9ctv': {'choices': [{'index': 7, 'label': 'Friends, family, or colleagues', 'score': 8},
                                   {'index': 8, 'label': 'MIT or Bootcamp alumni', 'score': 9},
                                   {'index': 9, 'label': 'MITx MicroMasters', 'score': 10},
                                   {'index': 10, 'label': 'EdX.org', 'score': 11}],
                       'identifier': None, 'name': 'How did you first hear about the Bootcamp?', 'other': False},
        'mKB692vrUs': {'choices': [{'index': 181, 'label': 'United Arab Emirates', 'score': 182},
                                   {'index': 182, 'label': 'United Kingdom', 'score': 183},
                                   {'index': 183, 'label': 'United States', 'score': 184}],
                       'identifier': None, 'name': 'Country/Region of Residence\n\n', 'other': False},
        'nM7vW8Laa4': {'choices': [{'index': 0, 'label': 'Male', 'score': 1},
                                   {'index': 1, 'label': 'Female', 'score': 2},
                                   {'index': 2, 'label': 'Other', 'score': 3}],
                       'identifier': None, 'name': 'Gender', 'other': False},
        'vHpRHIw9Xk': {'identifier': None, 'name': 'Company Name'},
        'vnPTughA3S': {'choices': [{'index': 0, 'label': 'Completed some high school', 'score': 1},
                                   {'index': 1, 'label': 'High school graduate', 'score': 2},
                                   {'index': 8, 'label': "Other advanced degree beyond a Master's degree",
                                    'score': 9}],
                       'identifier': None, 'name': 'Highest Level of Education', 'other': False},
        'xT6TFzHruM': {'identifier': None, 'name': 'Linkedin profile URL'},
        'xubvuT7xTq': {'identifier': None, 'name': 'Signature'},
        'y47FmfSdAl': {'choices': [{'index': 0, 'label': 'I Agree', 'score': 1}],
                       'identifier': None, 'name': 'Liability Release & Waiver', 'other': False}
    },
    'hide_until_prerequisites': False,
    'id': 677172,
    'index': 1,
    'instructions': '',
    'name': 'Part 1: Complete Your Application Form',
    'prerequisite_tasks': [],
    'required': True,
    'stage': {'id': 311343, 'title': 'Round 1 - Application Stage'},
    'type': 1,
    'updated_at': '2019-09-09T08:46:44',
    'view_before_eligible': True,
    'who_can_edit': 0
}

smapply_serialized_data = {
    'smapply_id': 123456, 'email': 'test_user@test.co', 'first_name': 'FirstName', 'last_name': 'LastName',
    'why_apply': 'Some kind of answer', 'alumni': 'No', 'industry': 'Arts and Crafts',
    'nationality': 'United States', 'referred_by': 'A person', 'date_of_birth': '1/1/1991',
    'work_experience': '10 years or more', 'other_programs': 'None okay', 'agree_see_links': 'I Disagree',
    'phone': '1234567890', 'jobtitle': 'Fake Job', 'participant_license_release': 'I Agree',
    'mit_honor_code': 'I Agree', 'occupation': 'Retired', 'confidentiality': 'I Agree',
    'referral_information': 'some kind of response', 'hear_about_bootcamp': 'MIT or Bootcamp alumni',
    'country': 'United States', 'gender': '', 'company': 'Fake Name',
    'highest_education': "Other advanced degree beyond a Master's degree",
    'linkedin_profile': 'https://www.linkedin.com', 'liability_release': 'I Agree'}


smapply_user_data = {
    'applicants_conflicted': 0,
    'applications_with_awarded_money_count': 0,
    'assignments_completed': 0,
    'assignments_total': 0,
    'awards_applied_to': [],
    'custom_fields': {'43316': ''},
    'date_joined': '2019-09-13T20:34:54',
    'date_joined_pretty': '4 days ago',
    'email': 'test_user@test.co',
    'first_name': 'FirstName',
    'full_name': 'FirstName LastName',
    'groups': [55624],
    'id': 105181281,
    'last_login': '2019-09-13T20:34:57',
    'last_login_pretty': '4 days ago',
    'last_name': 'LastName',
    'member_of': [],
    'organizations': [],
    'recommendations': [],
    'recommendations_completed': [],
    'role_ids': [1],
    'roles': 'Applicant',
    'signup_source': '-',
    'sso_id': [],
    'status': 0,
    'status_pretty': 'Active',
    'submissions': [],
    'team_names': '',
    'teams': [],
    'timezone': 'America/New_York',
    'verified': 'False'
}


@pytest.fixture
def demographics_data():
    """Make fixture out of demographics dict"""
    return copy.deepcopy(smapply_demographic_data)


@pytest.fixture
def task_data():
    """Make fixture out of task data dict"""
    return copy.deepcopy(smapply_task_data)


@pytest.fixture
def serialized_data():
    """Make fixture out of serialized demographics data"""
    return copy.deepcopy(smapply_serialized_data)


@pytest.fixture
def user_data():
    """Make fixture out of smapply user data"""
    return copy.deepcopy(smapply_user_data)


@pytest.fixture
def mock_hubspot_errors(mocker):
    """Mock the get_sync_errors API call, assuming a limit of 2"""
    yield mocker.patch(
        "hubspot.api.paged_sync_errors",
        side_effect=[error_response_json[0:2], error_response_json[2:]],
    )


@pytest.fixture
def mocked_celery(mocker):
    """Mock object that patches certain celery functions"""
    exception_class = TabError
    replace_mock = mocker.patch(
        "celery.app.task.Task.replace", autospec=True, side_effect=exception_class
    )
    group_mock = mocker.patch("celery.group", autospec=True)
    chain_mock = mocker.patch("celery.chain", autospec=True)

    yield SimpleNamespace(
        replace=replace_mock,
        group=group_mock,
        chain=chain_mock,
        replace_exception_class=exception_class,
    )


@pytest.fixture
def mock_logger(mocker):
    """ Mock the logger """
    yield mocker.patch("hubspot.tasks.log.error")


@pytest.fixture
def mock_hubspot_request(mocker):
    """Mock the send hubspot request method"""
    yield mocker.patch("hubspot.tasks.send_hubspot_request")


@pytest.fixture
def mock_hubspot_api_request(mocker):
    """Mock the send hubspot request method"""
    yield mocker.patch("hubspot.api.send_hubspot_request")
