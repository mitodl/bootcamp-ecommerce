"""Constants for the CMS app"""

BOOTCAMP_INDEX_SLUG = "bootcamps"


ACCEPTANCE_DEFAULT_LETTER_TEXT = """Dear {{ first_name }},

On behalf of the MIT Bootcamps Admissions Committee, I am delighted to inform you of your admission to the {{ bootcamp_name }} on {{ bootcamp_start_date }}. The cost of tuition for this Bootcamp is {{ price }}

You were selected from an outstanding pool of applicants based on the selection criteria: capacity for calculated risk, open and critical thinking, initiative with follow-through, and focus on community. MIT’s mission is to educate students in science and technology to best prepare them to solve the world’s greatest challenges.

You are invited to be a part of this mission.

If you choose to attend the {{ bootcamp_name }}, MIT is dedicated to providing you with an education that combines rigorous academic study with the excitement of discovery, support and intellectual stimulation in an intense, immersive experience. You will be pushed to your limits, inspired, challenged and supported by your peers, faculty, students, mentors and alumni from around the world.

It will be a life-changing experience.

Congratulations on your admission! I look forward to hearing from you and hope you can join us at the Bootcamp.
"""
REJECTION_DEFAULT_LETTER_TEXT = """Dear {{ first_name }},

After careful consideration, we regret to inform you that we are unable to proceed further in the admissions process for the {{ bootcamp_name }}. Based on our review, we believe you have the potential but are not ready at this time for the Bootcamp.

We hope you will take this as an opportunity to improve and re-apply at the next opportunity. Please read on to learn more about our process.

It was a tough decision. We select applicants who have a demonstrated capacity for calculated risk, open and critical thinking, initiative with follow through, and focus on community. Specifically, we offer admission to applicants that complement one another’s skillsets for this Bootcamp.

We found your story inspiring and liked the problems you’re trying to solve. We hope that you will continue working on it because the world needs entrepreneurs like you.

This is NOT a good-bye but rather a see you later.
"""

SAMPLE_DECISION_TEMPLATE_CONTEXT = {
    "first_name": "FirstName",
    "last_name": "LastName",
    "bootcamp_name": "Sample Bootcamp",
    "bootcamp_start_date": "July 1, 2136",
    "price": "$1987.65",
}
