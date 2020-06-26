Release Notes
=============

Version 0.46.4
--------------

- Fixed circular dependency with drawer components
- Fix rendering of homepage (#796)
- Handle failure to create jobma interview
- Added drawer close button and fixed drawer inconsistencies

Version 0.46.3 (Released June 26, 2020)
--------------

- Remove consumer_id, customer_account_id from Cybersource SA payload (#776)
- Fixed CMS admissions section links and fixed template vars

Version 0.46.2 (Released June 25, 2020)
--------------

- Fix resume link (#746)
- Add customer_account_id (#775)
- Fix a few small issues with the receipt email

Version 0.46.1 (Released June 25, 2020)
--------------

- hero image optional resource page
- Catalog grid spacing, alignment and notches - #718 #709
- product page feedback: insturctor carousel title fixes
- product page feedback: the margins between sections should be consistent, and larger
- Fixed app dashboard regression that prevented cards from expanding
- Migration conflict fix on master
- 404 and 500 page design (#742)
- Addressed Resource Page Feedback
- Remove CSS that changes letter spacing - #686
- update the favicon
- home page feedback, show full date, rather than its abbreviations
- home page feedback: add global community link
- product page: minor changes
- Fixed resume form to update correctly after upload
- Inline drf_datetime as a quick fix
- Limit to one Job per BootcampRun (#738)
- Fix miscellaneous account login/registration issues
- add review dashboard page
- Added receipt email
- Fix hubspot sync issues (#680)
- and  headers should be the same size (and same element) as the  header.
- add minor changes in program, alumni and admission section
- Fixed new application issues (available runs, empty message)
- Fixed learning resources template name
- Change page to section in CMS

Version 0.46.0 (Released June 24, 2020)
--------------

- Allow submission review decisions to be reversed (#676)
- Resume Drawer: upload file or linkedin url (#652)
- Get rid of recaptcha flex style (#705)
- Implement take video link (#659)
- View statement link should only show up if the user has made a payment (#692)
- Finalized nav bar
- Update validation email and create profile title (#663)

Version 0.45.3 (Released June 19, 2020)
--------------

- admission section title should be h2
- remove gray backgroun from social media icons
- Add link to bootcamp page on catalog card - #191
- Enable slugs on product page - #687
- Fixed flaky test
- Horizontal scroll on mobile width - fixes #674
- Catalog grid section - #163
- ProductPage: Fix styling issue
- product page feedback: carousel fixes
- Product page feedback: hero section updates

Version 0.45.2 (Released June 18, 2020)
--------------

- Payment history page (#627)
- moved resource pages under homepage
- Added remaining stuff for HomePage
- add migration for home page setup
- Fix the facet responses to avoid duplicate entries

Version 0.45.1 (Released June 16, 2020)
--------------

- Added feature flag for root/home page view
- Submission Review UI page (#620)
- open social links in the new tab
- Added new application UI
- Fix typo in Massachusetts (#655)

Version 0.45.0 (Released June 16, 2020)
--------------

- Fix for migration on homepage alumni section - #183
- Finished application detail UI in dashboard
- resource page structure
- Bootcamp index page and routing - #170
- Removed repeated footers
- Bump django from 2.2.10 to 2.2.13 (#628)
- Payment drawer (#618)
- reorder section
- Fix login state
- Global Alumni Section
- render cms site wide notifications in react
- Admissions section - #485
- - Program Elements Home Page
- Added admissions API for application steps
- Define site_name in template for resource and bootcamp run pages (#607)
- Home page base with header - #404

Version 0.44.1 (Released June 08, 2020)
--------------

- add the repl.py
- Pin test dependencies - #115
- Configured dashboard link to open profile drawer
- CMS: Bootcamp Program description
- Moved drawer rendering to top-level and removed temp page
- footer basic layout
- Added rough application detail view on dashboard
- personal price search and filter (#601)
- product page: add learning resource section
- Update profile page styling/layout (#575)

Version 0.44.0 (Released June 03, 2020)
--------------

- Fixed styling for deprecated landing page
- Add Linkedin option for resume (#577)
- Update login/registration UI to match designs (#537)
- Don't error on unexpected arguments in react view (#590)
- Added user application dashboard (list view)
- Get user info from API on payment page (#567)
- apply black formatting/checking (#581)

Version 0.43.1 (Released May 29, 2020)
--------------

- Add results_url from Jobma webhook (#580)
- update product page instruction section design
- add product page: alumni section

Version 0.43.0 (Released May 28, 2020)
--------------

- Update application state after Jobma webhook (#552)
- Change PaymentView to accept an application id instead of a run key (#561)
- Remove ADMISSION_* settings that are not used
- Remove redundant routes (#568)
- Refactor hubspot deal/line syncing (#546)
- add site-wide notification
- Fix DEFAULT_FILE_STORAGE value for S3 backend
- Updated overall site styling

Version 0.42.3 (Released May 27, 2020)
--------------

- Add checkout data API (#528)
- Add API for submitting review for application submissions (#526)

Version 0.42.2 (Released May 20, 2020)
--------------

- Add API for available bootcamp runs (#534)

Version 0.42.1 (Released May 19, 2020)
--------------

- Added newrelic to worker processes
- Modified application list view to only return applications that belong to the logged-in user

Version 0.42.0 (Released May 18, 2020)
--------------

- Minimal site topnav - #436
- Added endpoint to create a bootcamp application
- Remove duplicate function (#530)
- Move ecommerce-related views into ecommerce app (#525)
- Fix registration profile form (#517)
- Fix support links (#515)
- Added endpoint for fetching list of user applications
- Added endpoint for fetching detailed user application data
- Remove smapply and fluidreview apps (#500)

Version 0.41.0 (Released May 15, 2020)
--------------

- Fix duplicate color variable (#505)
- Redirect user to detail form if no legal address (#508)
- Bootcamp enrollments models (#486)
- Add support for uploading a resume to an existing application (#497)
- Backend changes for Bootcamp learning Area Page
- product page: add faculty section
- Add support for interview_link from Jobma (#496)
- add a basic drawer component
- Hubspot profile sync update (#488)
- Update hubspot contact sync code (#459)
- Fix accidental removal of pylint from pytest.ini (#495)
- Added internal API for starting applications and setting correct state
- Fix Jobma webhook permissions check (#489)
- Moved templatetags tests out of templatetags module to fix build
- Convert all tests to pytest (#480)
- Header section for product page - #441
- Front-end code for profiles, registration (#415)
- Bump wagtail from 2.8.1 to 2.8.2
- Moved application submission review fields
- Pin ddt dependency
- Fixed model admin, unique constraints, and added factories

Version 0.40.1 (Released May 11, 2020)
--------------

- pre_commit and detect-secrets (#422)
- Fixed 'Klass' reference in jobma app
- Initial work for supporting Jobma (#444)
- Renamed 'klass' model various code references
- Basic Bootcamp Run Page

Version 0.40.0 (Released May 06, 2020)
--------------

- Fix env var list parsing
- update sentry sdk
- Added bootcamp application models and admin
- Initial port of auth and related apps
- Fix environment variable for USE_S3, and remove reference to removed OverwriteStorage (#452)
- add zendesk customer support section in the footer
- Added resource pages in CMS

Version 0.39.2 (Released May 01, 2020)
--------------

- Upgraded docker-compose version and addedd Jupyter notebook config

Version 0.39.1 (Released April 30, 2020)
--------------

- Redirect to pay page after purchase (#426)
- Renamed 'bootcamp' app to 'main'
- Add redux-query and update API logic to use it (#417)

Version 0.39.0 (Released April 29, 2020)
--------------

- Add react-router, set up App.js (#412)
- Remove bootcamp admissions client (#396)
- Add Wagtail CMS (#407)

Version 0.38.1 (Released April 17, 2020)
--------------

- Upgraded deps (#382)
- Rename a couple UWSGI env vars, remove redundant if-env blocks (#387)

Version 0.38.0 (Released April 16, 2020)
--------------

- Update jsdom to fix security alert for cryptiles (#378)

Version 0.37.1 (Released April 13, 2020)
--------------

- Remove py-call-osafterfork setting from uwsgi.ini (#375)
- Upgrade node-sass for tar security alert (#376)
- Upgrade mocha (#373)

Version 0.37.0 (Released April 09, 2020)
--------------

- Upgrade css-loader for security alert for js-yaml (#372)
- Fix logout error 500 (#367)
- Bump merge from 1.2.0 to 1.2.1 (#370)
- Change application_stage from CharField to TextField to remove max_length (#365)
- Bump fstream from 1.0.11 to 1.0.12 (#369)
- Bump sshpk from 1.13.1 to 1.16.1 (#368)
- Bump is-my-json-valid from 2.17.1 to 2.20.0 (#344)
- Bump macaddress from 0.2.8 to 0.2.9 (#343)
- Bump nwmatcher from 1.4.3 to 1.4.4 (#342)
- Bump stringstream from 0.0.5 to 0.0.6 (#340)
- Bump django from 2.2.9 to 2.2.10 (#360)
- Bump codecov from 2.3.1 to 3.6.5 (#335)
- Add back SecurityMiddleware (#366)
- Upgrade minimist (#359)
- Add uWSGI settings (#358)

Version 0.36.0 (Released March 31, 2020)
--------------

- Upgrade django to 2.2.9 (#356)

Version 0.35.0 (Released March 23, 2020)
--------------

- Upgrade redux-asserts for security alert for lodash-es (#355)

Version 0.34.0 (Released March 10, 2020)
--------------

- Update prettier-eslint-cli and prettier-eslint (#348)

Version 0.33.1 (Released March 06, 2020)
--------------

- Add bootcamp name to deal (#350)

Version 0.33.0 (Released March 04, 2020)
--------------

- Hubspot contact serializer allow missing fields (#339)
- Update prettier-eslint to fix a security alert (#338)
- Update nyc for a security alert (#336)
- Pin potsgres version 9.6 -> 9.6.16

Version 0.32.0 (Released October 31, 2019)
--------------

- Only create profiles from userdata containing verified email addresses. (#326)

Version 0.31.1 (Released October 25, 2019)
--------------

- Sync contacts in bulk and add a retry to handle too many requests errors (#323)

Version 0.31.0 (Released October 23, 2019)
--------------

- Fix hubspot sync issues, update tests (#320)

Version 0.30.1 (Released October 15, 2019)
--------------

- Skip contact sync if message does not include email. Sync contact during smapply sync task (#314)

Version 0.30.0 (Released October 15, 2019)
--------------

- Fix attribute error (#312)
- Fix management command and handles multiple orders (#311)
- Add application stage field to hubspot deal (#310)
- Sync hubspot products, deals, and lines

Version 0.29.0 (Released October 14, 2019)
--------------

- Hubspot contact sync (#303)

Version 0.28.0 (Released October 09, 2019)
--------------

- Sync user demographics when app receives webhooks (#300)
- Add apllication_stage field to PersonalPrice (#299)
- Sync new SMApply users with local User and Profile models (#296)
- Update API requests to use newest API Apply Connect (#293)
- Peg test dependency versions (#295)
- README section for SMApply (#288)

Version 0.27.0 (Released July 25, 2019)
--------------

- update frontend dependencies (#279)

Version 0.26.0 (Released July 19, 2019)
--------------

- update backend packages (#280)

Version 0.25.0 (Released May 24, 2019)
--------------

- Update procfile

Version 0.24.0 (Released May 13, 2019)
--------------

- upgrade urllib3 (#270)

Version 0.23.0 (Released April 22, 2019)
--------------

- bump docker to use stretch

Version 0.22.0 (Released March 26, 2019)
--------------

- treat  as None for personal price

Version 0.21.0 (Released March 12, 2019)
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

