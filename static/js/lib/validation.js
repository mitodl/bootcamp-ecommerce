// @flow
import { __, includes } from "ramda"
import * as yup from "yup"
import {
  ADDRESS_LINES_MAX,
  CA_ALPHA_2,
  CA_POSTAL_CODE_REGEX,
  COUNTRIES_REQUIRING_STATE,
  NAME_REGEX,
  US_ALPHA_2,
  US_POSTAL_CODE_REGEX
} from "../constants"

// Field validations

export const emailFieldValidation = yup
  .string()
  .label("Email")
  .required()
  .email("Invalid email")

export const passwordFieldValidation = yup
  .string()
  .label("Password")
  .required()
  .min(8)

export const newPasswordFieldValidation = passwordFieldValidation.matches(
  /^(?=.*[0-9])(?=.*[a-zA-Z]).*$/,
  {
    message: "Password must contain at least one letter and number"
  }
)

export const resetPasswordFormValidation = yup.object().shape({
  newPassword:     newPasswordFieldValidation.label("New Password"),
  confirmPassword: yup
    .string()
    .label("Confirm Password")
    .required()
    .oneOf([yup.ref("newPassword")], "Passwords must match")
})

export const changePasswordFormValidation = yup.object().shape({
  oldPassword: yup
    .string()
    .label("Old Password")
    .required(),

  newPassword: newPasswordFieldValidation.label("New Password"),

  confirmPassword: yup
    .string()
    .label("Confirm Password")
    .required()
    .oneOf([yup.ref("newPassword")], "Passwords must match")
})

export const changeEmailFormValidation = yup.object().shape({
  email: emailFieldValidation.notOneOf(
    [yup.ref("$currentEmail")],
    "Email cannot be same, Use a different one"
  ),

  confirmPassword: passwordFieldValidation.label("Confirm Password")
})

export const legalAddressValidation = yup.object().shape({
  profile: yup.object().shape({
    name: yup
      .string()
      .label("Full Name")
      .trim()
      .required()
      .min(2)
  }),
  legal_address: yup.object().shape({
    first_name: yup
      .string()
      .label("First Name")
      .trim()
      .matches(NAME_REGEX, "Invalid First Name")
      .required(),
    last_name: yup
      .string()
      .label("Last Name")
      .trim()
      .matches(NAME_REGEX, "Invalid Last Name")
      .required(),
    city: yup
      .string()
      .label("City")
      .trim()
      .required(),
    street_address: yup
      .array()
      .label("Street address")
      .of(yup.string().max(60))
      .min(1)
      .max(ADDRESS_LINES_MAX)
      .compact()
      .required(),
    state_or_territory: yup
      .mixed()
      .label("State/Territory")
      .when("country", {
        is:   includes(__, COUNTRIES_REQUIRING_STATE),
        then: yup.string().required()
      }),
    country: yup
      .string()
      .label("Country")
      .length(2)
      .required(),
    postal_code: yup
      .string()
      .label("Zip/Postal Code")
      .trim()
      .when("country", (country, schema) => {
        if (country === US_ALPHA_2) {
          return schema.required().matches(US_POSTAL_CODE_REGEX, {
            message:
              "Postal Code must be formatted as either 'NNNNN' or 'NNNNN-NNNN'"
          })
        } else if (country === CA_ALPHA_2) {
          return schema.required().matches(CA_POSTAL_CODE_REGEX, {
            message: "Postal Code must be formatted as 'ANA NAN'"
          })
        }
      })
  })
})

export const passwordValidation = yup.object().shape({
  password: newPasswordFieldValidation
})

export const profileValidation = yup.object().shape({
  profile: yup.object().shape({
    gender: yup
      .string()
      .label("Gender")
      .required(),
    birth_year: yup
      .string()
      .label("Birth Year")
      .required(),
    company: yup
      .string()
      .label("Company")
      .trim()
      .required(),
    job_title: yup
      .string()
      .label("Job Title")
      .trim()
      .required(),
    industry: yup
      .string()
      .label("Industry")
      .required(),
    job_function: yup
      .string()
      .label("Job Function")
      .required(),
    company_size: yup
      .string()
      .label("Company Size")
      .required(),
    years_experience: yup
      .string()
      .label("Years of Work Experience")
      .required(),
    highest_education: yup
      .string()
      .label("Highest Level of Education")
      .required()
  })
})
