import React from "react"
import moment from "moment"
import { find, includes, propEq, range, reverse } from "ramda"
import { ErrorMessage, Field, FieldArray } from "formik"

import {
  ADDRESS_LINES_MAX,
  CA_ALPHA_2,
  COUNTRIES_REQUIRING_POSTAL_CODE,
  COUNTRIES_REQUIRING_STATE,
  EMPLOYMENT_EXPERIENCE,
  EMPLOYMENT_FUNCTION,
  EMPLOYMENT_INDUSTRY,
  EMPLOYMENT_SIZE,
  HIGHEST_EDUCATION_CHOICES,
  US_ALPHA_2
} from "../../constants"
import FormError from "./elements/FormError"

import type { Country } from "../../flow/authTypes"

const seedYear = moment().year()

type LegalAddressProps = {
  countries: Array<Country>,
  setFieldValue: Function,
  setFieldTouched: Function,
  values: Object,
  includePassword: boolean
}

export const LegalAddressFields = ({
  countries,
  setFieldValue,
  setFieldTouched,
  values,
  includePassword
}: LegalAddressProps) => (
  <React.Fragment>
    <div className="form-group">
      <label htmlFor="legal_address.first_name" className="row">
        <div className="col-4 font-weight-bold">First Name*</div>
      </label>
      <Field
        type="text"
        name="legal_address.first_name"
        className="form-control"
        autoComplete="given-name"
      />
      <ErrorMessage name="legal_address.first_name" component={FormError} />
    </div>
    <div className="form-group">
      <label htmlFor="legal_address.last_name" className="font-weight-bold">
        Last Name*
      </label>
      <Field
        type="text"
        name="legal_address.last_name"
        className="form-control"
        autoComplete="family-name"
      />
      <ErrorMessage name="legal_address.last_name" component={FormError} />
    </div>
    <div className="form-group">
      <label htmlFor="profile.name" className="row">
        <div className="col-4 font-weight-bold">Full Name*</div>
      </label>
      <Field
        type="text"
        name="profile.name"
        className="form-control"
        autoComplete="name"
      />
      <ErrorMessage name="profile.name" component={FormError} />
    </div>
    {includePassword ? (
      <div className="form-group">
        <label htmlFor="password" className="font-weight-bold">
          Password*
        </label>
        <Field type="password" name="password" className="form-control" />
        <ErrorMessage name="password" component={FormError} />
        <div className="label-secondary">
          Password must contain:
          <ul>
            <li>at least 8 characters</li>
            <li>at least 1 number and 1 letter</li>
          </ul>
        </div>
      </div>
    ) : null}
    <div className="form-group">
      {/* LegalAddress fields */}
      <label htmlFor="legal_address.street_address" className="row">
        <div className="col-4 font-weight-bold">Address*</div>
      </label>
      <FieldArray
        name="legal_address.street_address"
        render={arrayHelpers => (
          <div>
            <div key="0">
              <Field
                name={`legal_address.street_address[0]`}
                className={`form-control`}
                autoComplete={`address-line1`}
              />
              <ErrorMessage
                name="legal_address.street_address"
                component={FormError}
              />
            </div>
            {values.legal_address.street_address.map((line, index) =>
              index > 0 ? (
                <div key={index}>
                  <Field
                    name={`legal_address.street_address[${index}]`}
                    className={"form-control row-inner"}
                    autoComplete={`address-line${index + 1}`}
                  />
                </div>
              ) : null
            )}
            {values.legal_address.street_address.length < ADDRESS_LINES_MAX ? (
              <button
                type="button"
                className="additional-street"
                onClick={() => arrayHelpers.push("")}
              >
                Add additional line
              </button>
            ) : null}
          </div>
        )}
      />
    </div>
    <div className="form-group">
      <label htmlFor="legal_address.country" className="font-weight-bold">
        Country*
      </label>
      <Field
        component="select"
        name="legal_address.country"
        className="form-control"
        autoComplete="country"
        onChange={e => {
          setFieldValue("legal_address.country", e.target.value)
          setFieldTouched("legal_address.country")
          if (!includes(e.target.value, [US_ALPHA_2, CA_ALPHA_2])) {
            setFieldValue("legal_address.state_or_territory", "")
            setFieldValue("legal_address.postal_code", "")
          }
        }}
      >
        <option value="">-----</option>
        {countries ?
          countries.map((country, i) => (
            <option key={i} value={country.code}>
              {country.name}
            </option>
          )) :
          null}
      </Field>
      <ErrorMessage name="legal_address.country" component={FormError} />
    </div>
    {includes(values.legal_address.country, COUNTRIES_REQUIRING_STATE) ? (
      <div className="form-group">
        <label
          htmlFor="legal_address.state_or_territory"
          className="font-weight-bold"
        >
          State/Province*
        </label>
        <Field
          component="select"
          name="legal_address.state_or_territory"
          className="form-control"
          autoComplete="address-level1"
        >
          <option value="">-----</option>
          {find(
            propEq("code", values.legal_address.country),
            countries
          ).states.map((state, i) => (
            <option key={i} value={state.code}>
              {state.name}
            </option>
          ))}
        </Field>
        <ErrorMessage
          name="legal_address.state_or_territory"
          component={FormError}
        />
      </div>
    ) : null}
    <div className="form-group">
      <label htmlFor="legal_address.city" className="font-weight-bold">
        City*
      </label>
      <Field
        type="text"
        name="legal_address.city"
        className="form-control"
        autoComplete="address-level2"
      />
      <ErrorMessage name="legal_address.city" component={FormError} />
    </div>
    {includes(values.legal_address.country, COUNTRIES_REQUIRING_POSTAL_CODE) ? (
      <div className="form-group">
        <label htmlFor="legal_address.postal_code" className="font-weight-bold">
          Zip/Postal Code*
        </label>
        <Field
          type="text"
          name="legal_address.postal_code"
          className="form-control"
          autoComplete="postal-code"
        />
        <ErrorMessage name="legal_address.postal_code" component={FormError} />
      </div>
    ) : null}
  </React.Fragment>
)

export const ProfileFields = () => (
  <React.Fragment>
    <div className="form-group">
      <div className="row">
        <div className="col">
          <label htmlFor="profile.gender" className="font-weight-bold">
            Gender*
          </label>

          <Field
            component="select"
            name="profile.gender"
            className="form-control"
          >
            <option value="">-----</option>
            <option value="f">Female</option>
            <option value="m">Male</option>
            <option value="o">Other / Prefer not to say</option>
          </Field>
          <ErrorMessage name="profile.gender" component={FormError} />
        </div>
        <div className="col">
          <label htmlFor="profile.birth_year" className="font-weight-bold">
            Year of Birth*
          </label>
          <Field
            component="select"
            name="profile.birth_year"
            className="form-control"
          >
            <option value="">-----</option>
            {reverse(range(seedYear - 120, seedYear - 14)).map((year, i) => (
              <option key={i} value={year}>
                {year}
              </option>
            ))}
          </Field>
          <ErrorMessage name="profile.birth_year" component={FormError} />
        </div>
      </div>
    </div>
    <div className="form-group">
      <label htmlFor="profile.company" className="font-weight-bold">
        Company*
      </label>
      <Field type="text" name="profile.company" className="form-control" />
      <ErrorMessage name="profile.company" component={FormError} />
    </div>
    <div className="form-group">
      <label htmlFor="profile.job_title" className="font-weight-bold">
        Job Title*
      </label>
      <Field type="text" name="profile.job_title" className="form-control" />
      <ErrorMessage name="profile.job_title" component={FormError} />
    </div>
    <div className="form-group dotted" />
    <div className="form-group">
      <label htmlFor="profile.industry" className="font-weight-bold">
        Industry*
      </label>
      <Field
        component="select"
        name="profile.industry"
        className="form-control"
      >
        <option value="">-----</option>
        {EMPLOYMENT_INDUSTRY.map((industry, i) => (
          <option key={i} value={industry}>
            {industry}
          </option>
        ))}
      </Field>
      <ErrorMessage name="profile.industry" component={FormError} />
    </div>
    <div className="form-group">
      <label htmlFor="profile.job_function" className="font-weight-bold">
        Job Function*
      </label>
      <Field
        component="select"
        name="profile.job_function"
        className="form-control"
      >
        <option value="">-----</option>
        {EMPLOYMENT_FUNCTION.map((jobFunction, i) => (
          <option key={i} value={jobFunction}>
            {jobFunction}
          </option>
        ))}
      </Field>
      <ErrorMessage name="profile.job_function" component={FormError} />
    </div>
    <div className="form-group">
      <label htmlFor="profile.company_size" className="font-weight-bold">
        Company Size*
      </label>
      <Field
        component="select"
        name="profile.company_size"
        className="form-control"
      >
        <option value="">-----</option>
        {EMPLOYMENT_SIZE.map(([value, label], i) => (
          <option key={i} value={value}>
            {label}
          </option>
        ))}
      </Field>
      <ErrorMessage name="profile.company_size" component={FormError} />
    </div>
    <div className="form-group">
      <div className="row">
        <div className="col">
          <label
            htmlFor="profile.years_experience"
            className="font-weight-bold"
          >
            Years of Work Experience*
          </label>
          <Field
            component="select"
            name="profile.years_experience"
            className="form-control"
          >
            <option value="">-----</option>
            {EMPLOYMENT_EXPERIENCE.map(([value, label], i) => (
              <option key={i} value={value}>
                {label}
              </option>
            ))}
          </Field>
          <ErrorMessage name="profile.years_experience" component={FormError} />
        </div>
      </div>
    </div>
    <div className="form-group">
      <div className="row">
        <div className="col">
          <label
            htmlFor="profile.highest_education"
            className="font-weight-bold"
          >
            Highest Level of Education*
          </label>
          <Field
            component="select"
            name="profile.highest_education"
            className="form-control"
          >
            <option value="">-----</option>
            {HIGHEST_EDUCATION_CHOICES.map((level, i) => (
              <option key={i} value={level}>
                {level}
              </option>
            ))}
          </Field>
          <ErrorMessage
            name="profile.highest_education"
            component={FormError}
          />
        </div>
      </div>
    </div>
  </React.Fragment>
)
