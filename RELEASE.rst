Release Notes
=============

Version 0.21.0
--------------

- Change expected HTTP_AUTHORIZATION for smapply from OAuth to Basic (#262)
- Revert "update django-server-status, django, urllib3; remove pyyaml (#258)" (#260)
- update django-server-status, django, urllib3; remove pyyaml (#258)
- create klass title with award name instead of description

Version 0.20.0 (Released February 07, 2019)
--------------

- add validation for klass and bootcamp title

Version 0.19.0 (Released January 28, 2019)
--------------

- update message
- raise exception to sentry

Version 0.18.1 (Released December 26, 2018)
--------------

- Add name and url to email (#243)

Version 0.18.0 (Released December 07, 2018)
--------------

- Check SMA webhooks for awards (#245)
- Add Amount to Pay and Award Cost custom fields (#242)
- Turn off codecov status updates
- Added SMApply (#236)

Version 0.17.0 (Released November 15, 2018)
--------------

- update requirements (#237)

Version 0.16.0 (Released October 02, 2018)
--------------

- Create Bootcamp when award_id has no corresponding klass_key (#225)
- Added conformation dialog for over pay (#224)
- Add award id as parameter to success url (#221)

Version 0.15.0 (Released September 11, 2018)
--------------

- Pin docker images (#220)

Version 0.14.0 (Released September 06, 2018)
--------------

- Remove IS_OSX from env.sh (#218)
- Synchronized email address with email address from edX (#216)

Version 0.13.0 (Released June 05, 2018)
--------------

- Added django-hijack for user masquerading (#213)

Version 0.12.0 (Released April 23, 2018)
--------------

- Completely disabled overpayment error

Version 0.11.0 (Released March 14, 2018)
--------------

- Sort webhook requests by date
- Instructions on FluidReview webhook/trigger setup in README

Version 0.10.0 (Released February 22, 2018)
--------------

- Use award_cost as personal price if amount_to_pay is blank

Version 0.9.1 (Released January 30, 2018)
-------------

- Remove facebook pixel code, add google tag manager code
- Handle missing installments on payment page

Version 0.8.1 (Released January 19, 2018)
-------------

- Facebook pixel tracking

Version 0.8.0 (Released January 17, 2018)
-------------

- Raise exception if anything goes wrong with posting Webhook requests
- Ignore &#34;Accept&#34; header on requests to WebhookView

Version 0.7.0 (Released January 08, 2018)
-------------

- Fix port reference (#180)
- Use docker overrides for travis and local configuration differences (#174)
- Set default test client format (#175)
- JS upgrades (#173)
- Don&#39;t post payment until order is saved
- Update python to 3.6 (#172)

Version 0.6.1 (Released December 28, 2017)
-------------

- Post payment status to FluidReview
- Personal prices for klasses

Version 0.6.0 (Released December 21, 2017)
-------------

- case-insensitive email matching
- Look up admissions in WebhookRequest
- Update docstrings (#166)

Version 0.5.1 (Released December 13, 2017)
-------------

- Add SENTRY_LOG_LEVEL, default to ERROR (#160)
- Parse WebhookRequests, synchronize FluidReview and OAuth users

Version 0.5.0 (Released December 12, 2017)
-------------

- Fix root log handler (#158)
- Expand README, describe how to set up &amp; run Bootcamp
- Upgrade psycopg2 (#156)

Version 0.4.0 (Released December 06, 2017)
-------------

- Refactor BootcampAdmissionsClient (#149)
- Handle webhooks from FluidReview (#147)

Version 0.3.1 (Released December 01, 2017)
-------------

- OAuth requests for FluidReview API

Version 0.3.0 (Released November 29, 2017)
-------------

- footer css fix (#144)
- Remove BootcampAdmissionCache (#141)
- Use application logging level for Celery (#135)
- Use yarn install --frozen-lockfile (#134)

Version 0.2.1 (Released October 19, 2017)
-------------

- Added terms and conditions (#130)

Version 0.2.0 (Released October 10, 2017)
-------------

- Updated the yarn.lock after failed deployment
- remove models with migration
- removed models file
- remove models
- Update code with celery settings
- Deactivated reminder emails
- Moved js tests from payment container tests to component tests
- Fixed bug w/ &#39;no klasses&#39; message being shown while API results were still pending

Version 0.1.8 (Released June 16, 2017)
-------------

- remove stray period (#122)

Version 0.1.7 (Released June 15, 2017)
-------------

- text changes (#117)

Version 0.1.6 (Released June 14, 2017)
-------------

- Upgraded celery to 4

Version 0.1.5 (Released June 13, 2017)
-------------

- Upgraded requirements and fixed tests

Version 0.1.4 (Released June 12, 2017)
-------------

- Fixed bug in settings configuration 🤦

Version 0.1.3 (Released May 26, 2017)
-------------

- Fixed bug with &#39;no payment&#39; message

Version 0.1.2 (Released May 24, 2017)
-------------

- Added styling to error pages
- Added better configuration for klasses Admin
- Added message for users with no payment-eligible klasses
- Added Terms of Service page
- Change installation and payment deadline logic
- Fixed app.json

Version 0.1.1 (Released May 16, 2017)
-------------

- Removed installment number from the Installment
- Added automatic payment email reminders
- Removed integer keys from async_cache_admissions task (#94)
- Added klass payment statement
- smaller logo (#90)
- Fixed style of input page in Firefox
- Implemented order receipt/cancellation message (#81)
- Prevent users from making a payment if forbidden from paying for a klass (#83)
- Added navbar to bootcamp (#84)

Version 0.0.0 (Released May 10, 2017)
--------------

- First release

