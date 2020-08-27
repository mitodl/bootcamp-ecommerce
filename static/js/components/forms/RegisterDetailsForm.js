// @flow
/* global SETTINGS: false */
import React from "react"
import { clone } from "ramda"
import { Formik, Form } from "formik"

import {
  passwordValidation,
  legalAddressValidation
} from "../../lib/validation"
import { LegalAddressFields } from "./ProfileFormFields"
import ButtonWithLoader from "../loaders/ButtonWithLoader"

import type { Country, User } from "../../flow/authTypes"
import { isNilOrBlank } from "../../util/util"

type Props = {
  onSubmit: Function,
  countries: Array<Country>,
  includePassword: boolean,
  user?: User
}

const INITIAL_VALUES = {
  password:      "",
  legal_address: {
    first_name:         "",
    last_name:          "",
    street_address:     [""],
    city:               "",
    country:            "",
    state_or_territory: "",
    postal_code:        ""
  },
  profile: {
    name: ""
  }
}

const RegisterDetailsForm = ({
  onSubmit,
  countries,
  user,
  includePassword
}: Props) => {
  const initialValues =
    user && !isNilOrBlank(user) ? user : clone(INITIAL_VALUES)
  if (includePassword) {
    // $FlowFixMe
    initialValues.password = ""
  }
  return (
    <Formik
      onSubmit={onSubmit}
      validationSchema={legalAddressValidation.concat(
        includePassword ? passwordValidation : null
      )}
      initialValues={initialValues}
      render={({ isSubmitting, setFieldValue, setFieldTouched, values }) => (
        <Form>
          <LegalAddressFields
            countries={countries}
            setFieldValue={setFieldValue}
            setFieldTouched={setFieldTouched}
            values={values}
            includePassword={includePassword}
          />
          <div>
            <div className="required">*=Required</div>
            <div className="row submit-row no-gutters justify-content-end">
              <ButtonWithLoader
                type="submit"
                className="btn btn-outline-danger large-font"
                loading={isSubmitting}
              >
                Continue
              </ButtonWithLoader>
            </div>
          </div>
        </Form>
      )}
    />
  )
}

export default RegisterDetailsForm
