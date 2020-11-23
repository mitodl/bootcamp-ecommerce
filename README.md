# bootcamp-ecommerce
An app that allows users to apply for MIT Bootcamps, and admins to review those applications. 

**SECTIONS**
1. [Initial Setup](#initial-setup)
1. [Optional Setup](#optional-setup)

# Initial Setup

This app follows the same [initial setup steps outlined in the common ODL web app guide](https://github.com/mitodl/handbook/blob/master/common-web-app-guide.md).
Run through those steps **including the addition of `/etc/hosts` aliases**.

### Settings

Add the following settings in your `.env` file

```dotenv
# Replace this value with your own /etc/hosts alias for this app
BOOTCAMP_ECOMMERCE_BASE_URL=http://boot.odl.local
FEATURE_SOCIAL_AUTH_API=True
# Replace this with an email address you would like to set as the "from" address in Bootcamp emails
MAILGUN_FROM_EMAIL=your-email@example.com
# Replace this with an email address you would like all Bootcamp emails to go to
MAILGUN_RECIPIENT_OVERRIDE=your-email@example.com
# Ask a fellow developer for the values below, or pull them from one of our Heroku apps
MAILGUN_KEY=
MAILGUN_SENDER_DOMAIN=
```

### Configure the CMS

1. Run the management command to ensure the existence of some required CMS pages

   ```commandline
   docker-compose run --rm web ./manage.py configure_cms
   ```
1. Create the required CMS resource pages
    - Go to Settings > Resource Pages in the CMS
    - For each of the options, create a resource page and save these updated settings
    
### Run the app and create a user

1. Run the containers (`docker-compose up`)
1. Visit `/create-account` and follow the steps to create a new account, which includes
validating your email address from the email link and filling out a profile.
1. After your first user is created and the profile is filled out, set that user
as staff/superuser in a Django shell:

```python
USER_EMAIL="your_user@example.com"
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(email=USER_EMAIL).update(is_superuser=True, is_staff=True)
```  

# Optional Setup

### Third-part app settings

In order to get Cybersource integration working for completing test orders,
ask a fellow developer for these values or pull them from one of the non-production
Bootcamp Heroku apps:

```dotenv
CYBERSOURCE_ACCESS_KEY=
CYBERSOURCE_SECURITY_KEY=
CYBERSOURCE_TRANSACTION_KEY=
CYBERSOURCE_SECURE_ACCEPTANCE_URL=
CYBERSOURCE_PROFILE_ID=
CYBERSOURCE_REFERENCE_PREFIX=
```

In order to get video interviews working from your local app, ask a fellow developer 
for these values or pull them from one of the non-production Bootcamp Heroku apps:

```dotenv
JOBMA_ACCESS_TOKEN=
JOBMA_WEBHOOK_ACCESS_TOKEN=
JOBMA_BASE_URL=
```

### Seed data

Seed data can be generated via management command. It's designed to be idempotent, so running it multiple times 
should not create multiple sets of data.

```
docker-compose run --rm web ./manage.py seed_data
# To delete seed data
docker-compose run --rm web ./manage.py delete_seed_data
```

The logic for determining the state of a user's application and advancing them through each step is complicated enough 
that it's sometimes very annoying to test certain features. To help with this, there is a management command that 
you can use to force a user's application into a certain state:

```
docker-compose run --rm web ./manage.py set_application_state -i <your application id> --state <desired state>

# Examples:
docker-compose run --rm web ./manage.py set_application_state -i 123 --state AWAITING_PAYMENT
# Provide a user and run instead of a bootcamp application id
docker-compose run --rm web ./manage.py set_application_state --user me@example.com --run "Bootcamp Run 1" --state AWAITING_RESUME
```
