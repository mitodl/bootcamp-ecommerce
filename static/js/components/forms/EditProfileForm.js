// @flow
import React from "react"
import { pathOr } from "ramda"
import { Formik, Form } from "formik"

import { profileValidation, legalAddressValidation } from "../../lib/validation"
import { LegalAddressFields, ProfileFields } from "./ProfileFormFields"

import type { Country, CurrentUser } from "../../flow/authTypes"

type Props = {
  onSubmit: Function,
  countries: Array<Country>,
  user: CurrentUser
}

const getInitialValues = (user: CurrentUser) =>
  user.is_anonymous ?
    {} :
    {
      name:          user.name,
      email:         user.email,
      legal_address: user.legal_address,
      profile:       {
        ...user.profile,
        // Should be null but React complains about null values in form fields. So we need to convert to
        // string and then back to null on submit.
        gender:            pathOr("", ["gender"], user.profile),
        birth_year:        pathOr("", ["birth_year"], user.profile),
        job_function:      pathOr("", ["job_function"], user.profile),
        company_size:      pathOr("", ["company_size"], user.profile),
        industry:          pathOr("", ["industry"], user.profile),
        years_experience:  pathOr("", ["years_experience"], user.profile),
        highest_education: pathOr("", ["highest_education"], user.profile)
      }
    }

const EditProfileForm = ({ onSubmit, countries, user }: Props) => (
  <Formik
    onSubmit={onSubmit}
    validationSchema={legalAddressValidation.concat(profileValidation)}
    initialValues={getInitialValues(user)}
    render={({ isSubmitting, setFieldValue, setFieldTouched, values }) => (
      <Form>
        <div className="auth-header row">
          <h1 className="col-6">Profile</h1>
          <div className="col-6 profile-button-col">
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-danger profile-btn"
            >
              Save
            </button>
          </div>
        </div>
        <div className="auth-card card-shadow row">
          <div className="container">
            <div className="row">
              {user.is_authenticated ? (
                <div className="col-12 bootcamp-form">
                  <LegalAddressFields
                    countries={countries}
                    setFieldValue={setFieldValue}
                    setFieldTouched={setFieldTouched}
                    values={values}
                    includePassword={false}
                  />
                  <div className="divider"></div>
                  <ProfileFields />
                  <div className="row-inner justify-content-end">
                    <div className="required">*=Required</div>
                  </div>
                </div>
              ) : (
                <div className="row">
                  You must be logged in to edit your profile.
                </div>
              )}
            </div>
          </div>
        </div>
      </Form>
    )}
  />
)
export default EditProfileForm
