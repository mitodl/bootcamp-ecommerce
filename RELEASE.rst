Release Notes
=============

Version 0.117.0 (Released May 28, 2024)
---------------

- chore(deps): lock file maintenance
- fix(deps): update dependency django-cache-memoize to ^0.2.0
- fix(deps): update dependency dj-database-url to ^0.5.0
- chore(deps): update redis docker tag to v6.2.14
- chore(deps): update postgres docker tag to v11.16
- chore(deps): update node.js to v16.20.2
- chore(deps): update nginx docker tag to v1.26.0
- chore(deps): update docker.elastic.co/elasticsearch/elasticsearch docker tag to v6.8.23
- chore(deps): update dependency responses to ^0.25.0
- chore(deps): update dependency pytest-pylint to ^0.21.0
- chore(deps): update dependency pytest-env to ^0.8.0
- chore(deps): update dependency bpython to ^0.24
- chore(deps): lock file maintenance (#1534)
- fix: fix personal prices with unfulfilled orders (#1537)

Version 0.116.1 (Released April 22, 2024)
---------------

- Fix: Add nubbins for celery monitoring.
- Bump ipython from 7.31.1 to 8.10.0 (#1409)
- Bump http-cache-semantics from 4.1.0 to 4.1.1 (#1406)

Version 0.116.0 (Released April 17, 2024)
---------------

- chore(deps): lock file maintenance (#1528)
- chore(deps): update dependency black to v24.4.0
- fix(deps): update dependency wagtail to v5.2.4
- fix(deps): update dependency uwsgi to v2.0.25
- fix(deps): update dependency url-loader to v4.1.1
- fix(deps): update dependency react-zendesk to v0.1.13
- fix(deps): update dependency react-redux to v7.2.9
- fix(deps): update dependency prettier-eslint-cli to v5.0.1
- fix(deps): update dependency prettier-eslint to v9.0.2
- fix(deps): update dependency object.entries to v1.1.8
- fix(deps): update dependency named-urls to v2.0.1
- fix(deps): update dependency mutationobserver-shim to v0.3.7
- fix(deps): update dependency mini-css-extract-plugin to v1.6.2
- fix(deps): update dependency keycode to v2.2.1
- fix(deps): update dependency eslint-plugin-babel to v5.3.1
- fix(deps): update dependency django-fsm to v2.8.2
- fix(deps): update dependency boto3 to v1.34.84

Version 0.115.1 (Released April 10, 2024)
---------------

- add readable_id to bootcamp model and related changes (#1507)
- Bump es5-ext from 0.10.53 to 0.10.64 (#1494)

Version 0.115.0 (Released April 08, 2024)
---------------

- fix(deps): update dependency boto3 to v1.34.79 (#1463)
- fix(deps): update dependency decimal.js-light to v2.5.1 (#1469)
- fix(deps): update dependency enzyme-adapter-react-16 to v1.15.8 (#1470)
- Bump pillow from 10.2.0 to 10.3.0 (#1504)
- Bump minimist from 1.1.3 to 1.2.8 (#1506)
- Bump django from 3.2.23 to 3.2.25 (#1492)
- Bump cryptography from 41.0.5 to 42.0.4 (#1495)
- Bump pillow from 9.5.0 to 10.2.0 (#1496)
- Bump black from 22.12.0 to 24.3.0 (#1497)
- fix(deps): update dependency webpack-dev-middleware to v5 [security] (#1499)
- fix(deps): update dependency express to v4.19.2 [security]

Version 0.114.0 (Released April 01, 2024)
---------------

- chore: upgrade python to 3.10.13 (#1490)

Version 0.113.0 (Released March 21, 2024)
---------------

- feat(import_wire_transfers)!: use bootcamp run id in import_wire_transfers (#1491)

Version 0.112.1 (Released March 06, 2024)
---------------

- fix: dates display on the bootcamp cards (#1487)

Version 0.112.0 (Released February 26, 2024)
---------------

- style: update logo (#1484)
- fix(deps): update dependency mitol-django-hubspot-api to v2023.12.19
- chore(deps): update dependency pylint-django to ~2.5.0
- chore(deps): update dependency pylint to ~2.17.0

Version 0.111.0 (Released January 18, 2024)
---------------

- chore!: Upgrade wagtail to 5.2.1(latest) (#1472)

Version 0.110.0 (Released November 30, 2023)
---------------

- feat: add early bird deadline (#1468)
- fix: show review applications with future bootcamp run start date only (#1471)

Version 0.109.0 (Released November 16, 2023)
---------------

- feat: use poetry dependency management (#1456)

Version 0.108.0 (Released October 30, 2023)
---------------

- feat: add sponsors (#1454)
- Add renovate.json

Version 0.107.0 (Released July 25, 2023)
---------------

- feat: add a command to reset user's Jobma interview state (#1427)

Version 0.106.0 (Released June 01, 2023)
---------------

- Fix interaction between hubspot contact creation form and hubspot api contact sync (#1423)
- Bump cookiejar from 2.1.2 to 2.1.4 (#1403)
- Handle hubspot syncing for contacts w/multiple conflicting emails (#1419)

Version 0.105.0 (Released April 03, 2023)
---------------

- Call sync_hubspot_application if an order is successful but application is not paid in full (#1411)

Version 0.104.0 (Released January 30, 2023)
---------------

- Update node and jsdom (#1400)

Version 0.103.0 (Released January 23, 2023)
---------------

- Decorators for hubspt functions (#1399)
- Update README.md (#1401)
- Bump decode-uri-component from 0.2.0 to 0.2.2 (#1387)
- Bump loader-utils from 1.4.0 to 1.4.2 (#1382)
- Bump moment from 2.29.2 to 2.29.4 (#1358)
- Bump terser from 4.6.11 to 4.8.1 (#1353)
- Bump qs from 6.5.2 to 6.5.3 (#1388)
- Bump express from 4.17.1 to 4.17.3 (#1391)
- Bump json5 from 1.0.1 to 1.0.2 (#1395)
- Bump django from 3.2.14 to 3.2.16 (#1367)
- Bump pillow from 9.0.1 to 9.3.0 (#1384)
- Bump certifi from 2018.10.15 to 2022.12.7 (#1390)

Version 0.102.0 (Released January 11, 2023)
---------------

- Replace ubuntu-latest with ubuntu-22.04 (#1397)

Version 0.101.0 (Released January 05, 2023)
---------------

- Remove email validation (not necessary) from a hubspot sync function (#1394)

Version 0.100.1 (Released December 06, 2022)
---------------

- Add search to LineAdmin (#1385)

Version 0.100.0 (Released December 06, 2022)
---------------

- Hubspot CRM API syncing (#1374)

Version 0.99.2 (Released November 10, 2022)
--------------

- Fix: check for course admission page (#1380)
- Upgrade redis for M1 user

Version 0.99.1 (Released November 10, 2022)
--------------

- Feat: Allow users to specify bootcamp location in CMS (#1377)
- Remove an obsolete github workflow (#1371)

Version 0.99.0 (Released November 07, 2022)
--------------

- Bump lxml from 4.6.3 to 4.9.1 (#1352)

Version 0.98.1 (Released November 03, 2022)
--------------

- Upgrade celery, redis (#1370)

Version 0.98.0 (Released November 02, 2022)
--------------

- Bump pyjwt from 2.0.1 to 2.4.0 (#1348)

Version 0.97.0 (Released October 31, 2022)
--------------

- Update app.json
- Fix

Version 0.96.0 (Released September 07, 2022)
--------------

- Set python to 3.9.13 (#1359)
- Heroku-22 upgrade (#1357)

Version 0.95.0 (Released July 11, 2022)
--------------

- Bump django from 3.2.13 to 3.2.14 & update caniuse (#1350)

Version 0.94.1 (Released May 19, 2022)
--------------

- Added heroku deployment workflows

Version 0.94.0 (Released May 19, 2022)
--------------

- Bump django from 3.2.12 to 3.2.13 (#1339)
- asadiqbal08/Fix for Django model warning messages. (#1274)
- Bump moment from 2.24.0 to 2.29.2 (#1337)
- Bump ipython from 7.22.0 to 7.31.1 (#1335)

Version 0.93.0 (Released May 09, 2022)
--------------

- Bump urijs from 1.19.10 to 1.19.11 (#1338)

Version 0.92.1 (Released April 11, 2022)
--------------

- upgrade pillow to 9.0.1 (#1322)

Version 0.92.0 (Released April 06, 2022)
--------------

- Bump lodash-es from 4.17.15 to 4.17.21 (#1328)
- Bump urijs from 1.19.6 to 1.19.10 (#1327)
- Bump minimist from 1.2.5 to 1.2.6 (#1331)

Version 0.91.1 (Released March 29, 2022)
--------------

- chore: update git based package protocol (#1330)

Version 0.91.0 (Released March 14, 2022)
--------------

- Bump pathval from 1.1.0 to 1.1.1 (#1320)

Version 0.90.1 (Released January 31, 2022)
--------------

- Using djoser common functionality for password case insenitivity issue (#1317)

Version 0.90.0 (Released January 25, 2022)
--------------

- chore: bump pillow to 8.3.2 (#1312)

Version 0.89.0 (Released January 07, 2022)
--------------

- Bump path-parse from 1.0.6 to 1.0.7 (#1294)
- chore: update browserslist version (#1314)

Version 0.88.1 (Released November 10, 2021)
--------------

- Change references to Apply/Admissions to text entry fields in the CMS (#1308)
- fix error message when enrolling in 'Allows skipped steps' bootcamp that has no steps (#1310)

Version 0.88.0 (Released November 08, 2021)
--------------

- Remove Resume / LinkedIn URL step for webinar-style (no application steps) Bootcamps (#1301)

Version 0.87.0 (Released November 05, 2021)
--------------

- fix css issue of program description section steps rich text links (#1305)

Version 0.86.0 (Released November 01, 2021)
--------------

- Make a payment link for a bootcamp tied to the installment deadline (#1300)

Version 0.85.0 (Released October 13, 2021)
--------------

- Fix error message in defer_enrollment for missing enrollment (#1297)

Version 0.84.0 (Released July 29, 2021)
--------------

- Change NovoEd links to point directly to the desired course (#1263)

Version 0.83.1 (Released July 26, 2021)
--------------

- Update to use the common libraries from mitol-django (#1271)

Version 0.83.0 (Released July 19, 2021)
--------------

- add validation and proper error messages for LinkedIn URL (#1276)

Version 0.82.2 (Released July 13, 2021)
--------------

- migrate from node-sass to sass (#1279)

Version 0.82.1 (Released July 08, 2021)
--------------

- bump glob-parent to use 5.1.2 or above (#1281)

Version 0.82.0 (Released July 07, 2021)
--------------

- bump wagtail from 2.12.4 to 2.12.5 (#1278)

Version 0.81.2 (Released June 29, 2021)
--------------

- make a payment for (and therefore enroll in) a bootcamp with no application steps (#1272)

Version 0.81.1 (Released June 28, 2021)
--------------

- alert: upgrade mini-css-extract-plugin to resolve normalize-url alert (#1264)
- upgrade trim-lines to v3.0.1 (#1267)

Version 0.81.0 (Released June 23, 2021)
--------------

- Bump postcss from 7.0.27 to 7.0.36 (#1261)
- bump urllib3=1.26.5 through boto3 and requests (#1260)

Version 0.80.2 (Released June 14, 2021)
--------------

- upgrade django to 2.2.24 (#1258)

Version 0.80.1 (Released June 10, 2021)
--------------

- Bump browserslist from 4.11.1 to 4.16.6 (#1243)
- Bump ws from 7.2.3 to 7.4.6 (#1245)
- Don't fail CI if codecov upload fails

Version 0.80.0 (Released June 09, 2021)
--------------

- upgrade django to 2.2.21 (#1251)
- Bump Pillow to 8.2.0 & Wagtail to 2.12.4 (#1175)

Version 0.79.1 (Released June 03, 2021)
--------------

- defer enrollment (#1218)

Version 0.79.0 (Released June 02, 2021)
--------------

- Try to avoid localStorage error on mobile phones (#1227)

Version 0.78.6 (Released May 27, 2021)
--------------

- asadiqbal08/version bump property expr (#1225)

Version 0.78.5 (Released May 25, 2021)
--------------

- Set Application Review => Status to 'Pending' when waitlisting an application (#1241)

Version 0.78.4 (Released May 20, 2021)
--------------

- asadiqbal08/Update the merge package (#1224)

Version 0.78.3 (Released May 19, 2021)
--------------

- Updated bootcamp and order admin classes (#1234)

Version 0.78.2 (Released May 18, 2021)
--------------

- upgrade defusedxml version (#1235)

Version 0.78.1 (Released May 12, 2021)
--------------

- Bump hosted-git-info from 2.8.8 to 2.8.9 (#1230)
- Bump lodash from 4.17.19 to 4.17.21 (#1228)
- Bump ua-parser-js from 0.7.22 to 0.7.28 (#1223)

Version 0.78.0 (Released May 11, 2021)
--------------

- Upgrade to Python 3.9 (#1215)

Version 0.77.1 (Released May 03, 2021)
--------------

- Management command to retire users (#1205)

Version 0.77.0 (Released April 28, 2021)
--------------

- Upgrade djoser==2.1.0, djangoreseframework==3.11.2, social-auth-app-django==4.0.0 and dynamic-rest==2.0.0 (#1216)

Version 0.76.0 (Released April 20, 2021)
--------------

- Bump django-debug-toolbar from 1.11 to 1.11.1 (#1211)
- Bump ssri from 6.0.1 to 6.0.2 (#1212)
- Hide bootcamps with allow_skip_steps from users who are ineligible (#1196)
- deps: Updrage pip-tools, lxml and pygments (#1200)

Version 0.75.2 (Released April 16, 2021)
--------------

- Allow users who have paid for a bootcamp (in full) to skip application steps (#1206)

Version 0.75.1 (Released April 15, 2021)
--------------

- make import alumni case insensitive (#1202)

Version 0.75.0 (Released April 12, 2021)
--------------

- set can_skip_application_steps to True and unblock the certificate for the alumni (#1191)

Version 0.74.1 (Released April 12, 2021)
--------------

- Allow alumni to skip application steps (#1187)

Version 0.74.0 (Released April 06, 2021)
--------------

- Move the django logging level from DEBUG to INFO (#1192)

Version 0.73.1 (Released April 02, 2021)
--------------

- Adding bootcmp_run_id to products mapping and product information group in hubspot (#1189)
- Bump y18n from 4.0.0 to 4.0.1 (#1186)

Version 0.73.0 (Released April 01, 2021)
--------------

- Add bootcamp_run_id to BootcampRun model (#1178)

Version 0.72.0 (Released March 25, 2021)
--------------

- Upgrade caniuse-lite to fix breaking JS tests (#1177)
- import bootcamp alumni (#1171)
- Bump django from 2.2.13 to 2.2.18 (#1174)

Version 0.71.1 (Released March 12, 2021)
--------------

- Bump elliptic from 6.5.3 to 6.5.4 (#1169)

Version 0.71.0 (Released March 09, 2021)
--------------

- upgrade to 2.0.18
- Bump urijs from 1.19.4 to 1.19.6 (#1164)

Version 0.70.0 (Released February 25, 2021)
--------------

- Send compliance emails to ADMIN_EMAIL instead of EMAIL_SUPPORT (#1162)

Version 0.69.0 (Released February 16, 2021)
--------------

- #1155 display user's country in export compliance admin (#1156)
- Upgraded cryptography to 3.4.4

Version 0.68.1 (Released February 11, 2021)
--------------

- Upgrade Deps, immer to 8.0.1 & pysaml2 to 6.5.1 (#1154)

Version 0.68.0 (Released February 10, 2021)
--------------

- Wiretransfer: update data for existing orders

Version 0.67.0 (Released February 04, 2021)
--------------

- Wiretransfer: after data is imported, update the application state (#1148)
- 1019 Wiretransfer: Fix datetime timezone warnings during import_wire_transfers
- Admin: Added Bootcamp run filter on BootcampRunEnrollment
- Block/UnBlock list of users for getting certificates.  (#1142)

Version 0.66.0 (Released January 21, 2021)
--------------

- Fixed external bootcamp link icon positioning in dashboard (#1144)

Version 0.65.0 (Released January 13, 2021)
--------------

- Ignore submit, do not throw error, if partial token is null (#1134)
- Fixed application state for personal prices set to zero (#1133)
- upgrade lxml to v4.6.2 (#1139)
- quiet CSOURCE_PAYLOAD error (#1137)
- make signatory_images mandatory (#1136)

Version 0.64.1 (Released January 07, 2021)
--------------

- fixes in certificate template context (#1128)
- Make sure waait is compiled to ES5 (#1124)
- #1125 Certificates: don't abbreviate dates

Version 0.64.0 (Released January 06, 2021)
--------------

- Bump urijs from 1.19.2 to 1.19.4
- Certificate Page template Integration (#1116)
- cetificate command tests (#1118)
- certificates unittest for cms and klass models
- add certificate link to user dashboard (#1114)
- add certificate management commands (#1111)
- adding certificate routing and basic context (#1110)
- relabeling the fields and default values
- Wagtail CMS changes for bootcamp certificate
- Bootcamp run certificate models changes
- Added field validation on first and last name (#1096)
- add dynamic cache controlling via env variable (#1099)
- Bump ini from 1.3.5 to 1.3.7 (#1098)

Version 0.63.2 (Released December 21, 2020)
--------------

- Fixed buggy personal price adjustment behavior (#1094)

Version 0.63.1 (Released December 07, 2020)
--------------

- Added logic to fetch bootcamp runs by display title in mgmt commands (#1089)

Version 0.63.0 (Released December 01, 2020)
--------------

- Fixed file handling for set_application_state command (#1088)
- Added 'state' param to migrate_applications command (#1079)

Version 0.62.0 (Released November 25, 2020)
--------------

- Added flag to run python tests only without pylint/cov/warnings (#1085)
- Added seed data command for setting application state (#1084)
- Replacing Travis with Github actions and using pytest instead of tox (#1086)

Version 0.61.2 (Released November 24, 2020)
--------------

- Add OWASP ZAP security scan with Github action (#1080)

Version 0.61.1 (Released November 18, 2020)
--------------

- Added command to migrate applications from one run to another (#1077)

Version 0.61.0 (Released November 17, 2020)
--------------

- cryptography version update from 3.1 to 3.2.1

Version 0.60.1 (Released October 29, 2020)
--------------

- fixing copy revision bug

Version 0.60.0 (Released October 27, 2020)
--------------

- Changed NovoEd API to update the sync date if a NovoEd enrollment already exists (#1058)
- add copy bootcamp feature

Version 0.59.2 (Released October 26, 2020)
--------------

- Filter submissions by run instead of bootcamp (#1063)

Version 0.59.1 (Released October 22, 2020)
--------------

- Added cms-login to bootcamp-login redirection (#1060)

Version 0.59.0 (Released October 21, 2020)
--------------

- node-fetch dependency upgrade to version 2.6.1
- Prevented payment if bootcamp run start date is in the past (#1052)

Version 0.58.1 (Released October 16, 2020)
--------------

- Changed SAML config to use different identifiers for staging (#1051)

Version 0.58.0 (Released October 14, 2020)
--------------

- Updated node deps to support yargs-parser-13.1.2

Version 0.57.6 (Released October 09, 2020)
--------------

- Added NovoEd link to title in collapsed dashboard card (#1044)
- fixing variable name exceptions
- Show payment error message (#1039)

Version 0.57.5 (Released October 07, 2020)
--------------

- Added link to NovoEd from application dashboard (#1041)
- Updated caniuse-lite (#1042)

Version 0.57.4 (Released October 02, 2020)
--------------

- Added setting for overriding SESSION_ENGINE (#1037)

Version 0.57.3 (Released October 02, 2020)
--------------

- Added setting for overriding base SAML URL (#1034)

Version 0.57.2 (Released October 02, 2020)
--------------

- Configured IdP for NovoEd to enable login via SAML (#1015)

Version 0.57.1 (Released October 01, 2020)
--------------

- Optimize Profile and Home page context
- Add admin for WireTransferReceipt (#1021)

Version 0.57.0 (Released September 30, 2020)
--------------

- add filter for payment type in admin order
- fixes mailing address formatting

Version 0.56.0 (Released September 23, 2020)
--------------

- Handle wire transfers (#924)

Version 0.55.3 (Released September 23, 2020)
--------------

- remove navbar and footer from the print version of the payment statements

Version 0.55.2 (Released September 16, 2020)
--------------

- Updated Heroku nginx config and Django settings for file upload size (#1004)
- Added NovoEd integration for adding/removing enrollments (#1002)

Version 0.55.1 (Released September 15, 2020)
--------------

- Add support for sticky notifications (#993)
- Add a try..except block to refresh_pending_interview_links (#1006)
- Fixed react-dropzone-uploader bugs (#996)
- Check for and fix missing submissions & null interview urls (#1000)

Version 0.55.0 (Released September 09, 2020)
--------------

- update receipt for refunds

Version 0.54.1 (Released September 04, 2020)
--------------

- Add loaders for API requests (#987)
- Remove Payment component, used in the previous version of this application (#989)

Version 0.54.0 (Released September 04, 2020)
--------------

- fix serialize-javascript security alert

Version 0.53.0 (Released August 31, 2020)
--------------

- Create codeql-analysis.yml (#986)
- remove run key from line
- Allow user to retry cybersource compliance validation (#969)

Version 0.52.3 (Released August 24, 2020)
--------------

- Allow users to update resume until submission is reviewed (#963)
- Quiet template absent variable errors - #974
- Update Line to join by bootcamp_run_id

Version 0.52.2 (Released August 21, 2020)
--------------

- add implementation for letter template page customized signatory details

Version 0.52.1 (Released August 20, 2020)
--------------

- change recpatcha script domain (#976)
- Updated configure_cms mgmt command to create resource and letter template - #882

Version 0.52.0 (Released August 19, 2020)
--------------

- set user.is_active to False on creation (#978)
- add cache-control header to hash.txt and api urls (#944)
- Add signatory name and signature customization options for acceptance/rejection letter

Version 0.51.1 (Released August 17, 2020)
--------------

- Refresh old interview links (#959)
- Send IP address to cybersource (#955)
- Fixes button styles issues

Version 0.51.0 (Released August 07, 2020)
--------------

- Fix terms link on payment drawer (#957)
- Bump elliptic from 6.5.2 to 6.5.3
- admin section, make details top aligned
- add a Accessibility link in footer

Version 0.50.3 (Released August 03, 2020)
--------------

- Update pillow version
- Release date for 0.50.2
- New full_name field for hubspot (#941)
- Bump codecov from 3.6.5 to 3.7.1 (#935)
- Bump wagtail from 2.9.2 to 2.9.3 (#936)
- Bump lodash from 4.17.15 to 4.17.19 (#929)

Version 0.50.2 (Released July 28, 2020)
--------------

- Updated readme (#939)

Version 0.50.1 (Released July 22, 2020)
--------------

- Added seed data scripts and commands (#927)

Version 0.50.0 (Released July 21, 2020)
--------------

- Filter out submissions that cannot be reviewed (#932)
- Upgrade wagtail - #900
- More admin improvements, including receipt class fix (#928)
- fix mobile margin (#925)
- Various improvements to django admin classes

Version 0.49.0 (Released July 15, 2020)
--------------

- fix anchor-tag related accessibility issues on dashboard
- Implemented consistent error and success behavior
- conditional hubspot/zendesk JS (#917)
- CMS model tests
- Paging for submission reviews (#905)

Version 0.48.3 (Released July 15, 2020)
--------------

- fix dropzone accessibility issue
- Allow refunds for users without enrollments (partial payments) (#910)
- legal address requirement (#895)
- cms pages feedback

Version 0.48.2 (Released July 09, 2020)
--------------

- Fix caching for resource page links
- Add label for Refunded (#904)

Version 0.48.1 (Released July 09, 2020)
--------------

- Refund management command (#806)

Version 0.48.0 (Released July 07, 2020)
--------------

- Don't prefetch interview which doesn't exist on QuizSubmission (#891)
- Fixed sticky footer (#890)
- remove payment page (#852)
- load legacy hubspot js for older browsers as shown in hubspot sample embed code, use target div (#867)
- Fix invalid HTML tag (#876)
- Simplify review submission serializer (#865)
- Better formatting for negative formatPrice (#862)
- fix aria-labelledby value for accessiblity issue
- Pin isort to fix master
- Added 'split-on-first' library to loader config
- Added min space above footer and made it 'sticky'
- Removed ES6 template literal in Django template
- Logo file resize - #808

Version 0.47.4 (Released July 02, 2020)
--------------

- Fixes faulty logic in Profile.is_complete
- Fixed payment input validation

Version 0.47.3 (Released July 02, 2020)
--------------

- Added rule to transpile query-string library + dependency
- Fixed address factory (which caused flaky username test)

Version 0.47.2 (Released July 01, 2020)
--------------

- Added setting for USE_X_FORWARDED_HOST

Version 0.47.1 (Released June 30, 2020)
--------------

- Allow any page for bootcamp programs page
- Display interview token in take video interview drawer (#839)
- Cleaned up tos / privacy policy link usage
- Add 'static' to letter template signature url (#834)
- Remove "View your video" link on application
- tweak retry_invalid_line_associations function (#821)
- Make take interview link open in a separate tab (#817)
- Add interview_token (#835)
- Hubspot Footer Form With Arrow Button.
- Update the link styling for all links to match InVision on both home and product page
- update footer styling, backgorund-color etc.
- Fixed thumbnail stretching in application dashboard
- gray link in program elements section

Version 0.47.0 (Released June 30, 2020)
--------------

- Acceptance/rejection letters (#744)
- fix some accessibility issues on the application dashboard
- Fix formatting for negative zero (#807)
- Fix: object has no attribute 'id'
- Fix personal price calculation (#805)
- Sync product (bootcamp run) on transaction commit (#759)
- back to top accessibility fix
- Safari CSS issue fix - #771

Version 0.46.5 (Released June 26, 2020)
--------------

- fix review dashbard paging behavior
- fix review dashboard refreshing behavior
- Fixed text overflow issue with custom select component

Version 0.46.4 (Released June 26, 2020)
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

