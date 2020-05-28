// @flow
import React from "react"
import { Formik, Form } from "formik"

import {
  passwordValidation,
  legalAddressValidation
} from "../../lib/validation"
import { LegalAddressFields } from "./ProfileFormFields"

import type { Country } from "../../flow/authTypes"

type Props = {
  onSubmit: Function,
  countries: Array<Country>
}

const INITIAL_VALUES = {
  password:      "",
  legal_address: {
    first_name:         "",
    last_name:          "",
    street_address:     ["", ""],
    city:               "",
    country:            "",
    state_or_territory: "",
    postal_code:        ""
  },
  profile: {
    name: ""
  }
}

const RegisterDetailsForm = ({ onSubmit, countries }: Props) => (
  <Formik
    onSubmit={onSubmit}
    validationSchema={legalAddressValidation.concat(passwordValidation)}
    initialValues={INITIAL_VALUES}
    render={({ isSubmitting, setFieldValue, setFieldTouched, values }) => (
      <Form>
        <LegalAddressFields
          countries={countries}
          setFieldValue={setFieldValue}
          setFieldTouched={setFieldTouched}
          values={values}
          includePassword={true}
        />
        <div>
          <div className="required">*=Required</div>
          <div className="row submit-row no-gutters justify-content-end">
            <button
              type="submit"
              className="btn btn-outline-danger large-font"
              disabled={isSubmitting}
            >
              Continue
            </button>
          </div>
        </div>
      </Form>
    )}
  />
)

export default RegisterDetailsForm
