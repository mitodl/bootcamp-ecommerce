# bootcamp-ecommerce
MIT Bootcamp e-commerce

## Major Dependencies
- Docker
  - [Download from Docker website](https://docker.com/). Follow the OS X or Linux instructions depending on your OS.
- [Virtualbox](https://www.virtualbox.org/wiki/Downloads) to run edX locally


## Running edX devstack locally

#### 1) Create your edx docker container with at least 4G memory, and make note of the IP address:

    docker-machine create --virtualbox-memory "4096" edx
    eval $(docker-machine env edx)


#### 2) Follow the instructions for running EdX in a Docker environment here:

     https://github.com/edx/devstack/blob/master/README.rst


#### 3) Add an OAuth client

Wait a minute or two for the EdX container to complete startup.
Go to the Django admin page for Edx, login as the "edx" user (password is "edx"),
navigate to the Django OAuth Toolkit section at `/admin/oauth2_provider/`,
and add a new Application. Fill in the values as follows:

- **User**: Use the lookup (magnifying glass) to find your superuser
- **Redirect uris**: The URL where Bootcamp will be running, followed by "/complete/edxorg/".
  - **Linux users:** the Bootcamp URL will be `http://localhost:8099`.
  - **OSX users:** The Bootcamp IP can be found by running ``docker-machine ip <machine_name>`` from the host machine.
  - Bootcamp runs on port ``8099`` by default, so the full URL should be something like
 ``http://192.168.99.100:8099/complete/edxorg/``
- **Client type**: Set to '_Confidential_'.
- **Authorization grant type**: Set to '_Authorization Code_'.
- **Name**: Anything you want. Something like 'bc-local' would do fine here.

## Running Bootcamp locally

#### 1) Create your docker container for Bootcamp:

The following commands create a Docker machine named ``bootcamp``, start the
container, and configure environment variables to facilitate communication
with the edX instance. Do this in a separate shell from the one that EdX runs on and note the IP address.

    docker-machine create bootcamp
    eval $(docker-machine env bootcamp)


#### 2) Clone the repository and navigate to the bootcamp-ecommerce directory.


#### 3) Copy relevant values to use in the Bootcamp .env file

The Bootcamp codebase contains a ``.env.example`` file which will be used as
a template to create your ``.env`` file. For Bootcamp to work, it needs 6 values:

- ``EDXORG_BASE_URL``

    This value _should_ be ``http://<EDX_DOCKER_MACHINE_IP>:18000``. The IP will be that of your edx docker-machine.

- ``EDXORG_CLIENT_ID`` and ``EDXORG_CLIENT_SECRET``

    These values can be found in the Django OAuth Toolkit Application you created above.

- ``BOOTCAMP_ADMISSION_BASE_URL`` - A site on heroku, ask a Bootcamp developer for the URL

- ``BOOTCAMP_ADMISSION_KEY`` - Ask a Bootcamp developer for it.

- ``BOOTCAMP_ECOMMERCE_BASE_URL`` -

    The URL of your bootcamp instance on Docker (``http://<BOOTCAMP_DOCKER_MACHINE_IP>:8099``)


#### 4) Build and start the containers

    docker-compose build
    docker-compose up


#### 5) Create a superuser

    docker-compose run web python manage.py createsuperuser


#### 6) Find out which klasses user staff@example.com is enrolled in:

    http://<BOOTCAMP_ADMISSION_BASE_URL>/api/v1/user/?email=staff@example.com&key=<BOOTCAMP_ADMISSION_KEY>


#### 7) Log in to bootcamp as a superuser and create necessary objects in the admin console (../admin):
  - Create a bootcamp at `/admin/klasses/bootcamp/add/`
  - Create a klass for that bootcamp with a key that matches a klass returned in Step 6
  - Create an installment for the klass at `/admin/klasses/installment/add/`
  - Log out


#### 8) Go to the home page of your bootcamp site and login via EdX
  - Log in as staff@example.com (password: edx).
  - You should see a message that you owe the amount of money equal to the installment you created in step 6.


## Integration with FluidReview

#### 1) Set FluidReview environment variables
Values for the first four can be found at `<FLUIDREVIEW_BASE_URL>/admin/developer/` on the FluidReview site.
  - `FLUIDREVIEW_CLIENT_ID`
  - `FLUIDREVIEW_CLIENT_SECRET`
  - `FLUIDREVIEW_ACCESS_TOKEN`
  - `FLUIDREVIEW_REFRESH_TOKEN`
  - `FLUIDREVIEW_BASE_URL` (the FluidReview site URL)
  - `FLUIDREVIEW_WEBHOOK_AUTH_TOKEN` (a manually assigned value that is difficult to guess)
  
#### 2) Create a trigger in FluidReview
  - Go to `<FLUIDREVIEW_BASE_URL>/admin/triggers/`
  - Click `New Trigger`
  - Activation: set to `Submissions: A submission has been promoted to a new stage`
  - Conditions: set to `Submission is in stage`, `is exactly`, `Accepted Applications`
  - Add action `Advanced Webhook`
    - URL: `<BOOTCAMP_BASE_URL>/api/v0/fluidreview_webhook/`
    - Method: `POST`
    - Auth Token: `<FLUIDREVIEW_WEBHOOK_AUTH_TOKEN>`
    - Request content: 
        ```
        {
          "date_of_birth": "{{ submission.var__155310__BzgWgZZxIk }}",
          "user_email": "{{ submission.email }}",
          "amount_to_pay": "{{ submission.field__27006 }}",
          "user_id": {{ submission.user.id }},
          "submission_id": {{ submission.id }},
          "award_id": {{ award.id }},
          "award_cost": "{{ award.field__27157 }}",
          "award_name": "{{ award.name }}"
        }
        ```
  - Priority: 1
  - Status: Active
  
## Integration with SMApply

#### 1) Set SMApply environment variables
  - `SMAPPLY_CLIENT_ID`
  - `SMAPPLY_CLIENT_SECRET`
  - `SMAPPLY_ACCESS_TOKEN`
  - `SMAPPLY_REFRESH_TOKEN`
  - `SMAPPLY_BASE_URL` (the SMApply site URL)
  - `SMAPPLY_WEBHOOK_AUTH_TOKEN` (a manually assigned value that is difficult to guess)
  - `SMAPPLY_AMOUNTPAID_ID` (SMapply id for 'Amount Paid' custom field)
  - `SMAPPLY_AMOUNT_TO_PAY_ID` (SMapply id for 'Amount To Pay' custom field)
  - `SMAPPLY_AWARD_COST_ID` (SMapply id for 'Award Cost' custom field)

Values for the first four can be found at `<SMAPPLY_BASE_URL>/admin/settings/integrations/api/` on the SMApply site.
Custom fields can be found at `<SMAPPLY_BASE_URL>/admin/settings/metadata/`
  
  
#### 2) Create a trigger in SMApply
  - Go to `<SMAPPLY_BASE_URL>/admin/awards/<bootcamp_id>/automations/`
  - Create or edit an automation
  - Fill out the "When to Apply" and/or "Conditions" sections as needed
  - Fill out "Do the following actions":
    - Choose 'Integrations -> Fire webhook' from the dropdown
    - URL: `<BOOTCAMP_BASE_URL>/api/v0/smapply_webhook/`
    - Method: `POST`
    - Auth Token: `<SMAPPLY_WEBHOOK_AUTH_TOKEN>`
    - Sample request content sent by the webhook will be something like: 
        ```
        {
          "status": 1,
          "user_id": 99119890,
          "title": "0000000007",
          "award": 88562,
          "additional_content": "",
          "reference_id": "0000000007",
          "date_created": "Nov 8 2018 06:25 PM",
          "last_edited": "Nov 8 2018 06:28 PM",
          "id": 6903908,
          "round": 88368,
          "user": "Student Name"
        }
        ```
