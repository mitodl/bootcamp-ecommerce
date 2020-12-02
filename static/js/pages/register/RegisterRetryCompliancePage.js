// @flow
/* global SETTINGS: false */
import React from "react"
import {
  CS_DEFAULT_MESSAGE,
  REGISTER_DETAILS_PAGE_TITLE
} from "../../constants"
import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"
import { connectRequest } from "redux-query-react"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import auth from "../../lib/queries/auth"
import { STATE_ERROR, handleAuthResponse } from "../../lib/auth"
import queries from "../../lib/queries"
import {
  qsBackendSelector,
  qsErrorCodeSelector,
  qsPartialTokenSelector
} from "../../lib/selectors"
import { formatTitle, isNilOrBlank, transformError } from "../../util/util"

import RegisterDetailsForm from "../../components/forms/RegisterDetailsForm"

import type { RouterHistory, Location } from "react-router"

import type {
  AuthResponse,
  LegalAddress,
  Country,
  HttpAuthResponse,
  PartialProfile,
  User
} from "../../flow/authTypes"

type RegisterProps = {|
  location: Location,
  history: RouterHistory,
  params: { partialToken: string, backend: string, errors: string }
|}

type StateProps = {|
  countries: Array<Country>
|}

type DispatchProps = {|
  registerDetails: (
    name: string,
    legalAddress: LegalAddress,
    partialToken: string,
    backend: string
  ) => Promise<HttpAuthResponse<AuthResponse>>
|}

type Props = {|
  ...RegisterProps,
  ...StateProps,
  ...DispatchProps
|}

type State = {
  user: ?User
}

export class RegisterRetryCompliancePage extends React.Component<Props, State> {
  state = {
    user: null
  }

  async componentDidMount() {
    const {
      registerDetails,
      history,
      params: { partialToken, backend }
    } = this.props
    const { body } = await registerDetails(
      // $FlowFixMe
      null,
      // $FlowFixMe
      null,
      partialToken,
      backend
    )

    if (!isNilOrBlank(body.errors)) {
      // there is still a compliance issue, set user data in state
      this.setState({ user: body.extra_data })
    } else {
      // compliance check just passed, nothing to see here, move along
      handleAuthResponse(history, body, {})
    }
  }

  async onSubmit(detailsData: any, { setSubmitting, setErrors }: any) {
    const {
      history,
      registerDetails,
      params: { partialToken, backend }
    } = this.props
    try {
      // $FlowFixMe
      const { body } = await registerDetails(
        detailsData.profile,
        detailsData.legal_address,
        partialToken,
        backend
      )

      handleAuthResponse(history, body, {
        // eslint-disable-next-line camelcase
        [STATE_ERROR]: ({ field_errors }: AuthResponse) =>
          setErrors(field_errors)
      })
    } finally {
      setSubmitting(false)
    }
  }

  getTransformedErrorMessage(errors: string) {
    // Clean the error string
    const errorsList = errors
      .trim()
      .replace("Error code: ", "")
      .split(",")
    const errorMessage = "There was a problem validating your profile: "
    // Populate a list of transformed error messages
    const transformedErrors = []
    errorsList.map(errorCode => {
      transformedErrors.push(`*${transformError(errorCode)}`)
    })
    // Proper error message
    if (transformedErrors.length === 0) return errorMessage + CS_DEFAULT_MESSAGE

    return errorMessage + transformedErrors.join(", ")
  }

  render() {
    const {
      countries,
      params: { errors }
    } = this.props
    const { user } = this.state
    return countries && user ? (
      <div className="container auth-page registration-page">
        <MetaTags>
          <title>{formatTitle(REGISTER_DETAILS_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="row auth-header">
          <h1 className="col-12">{REGISTER_DETAILS_PAGE_TITLE}</h1>
        </div>
        <div className="bootcamp-form auth-card card-shadow row">
          <div className="col-12 auth-step">Steps 1 of 2</div>
          {!isNilOrBlank(errors) && (
            <div className="col-12 text-danger">
              <p>
                {this.getTransformedErrorMessage(errors)}.
                <br /> If this happens more than once, please contact{" "}
                <a
                  href={SETTINGS.support_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  customer support
                </a>
                .
              </p>
            </div>
          )}
          <div className="col-12">
            <RegisterDetailsForm
              onSubmit={this.onSubmit.bind(this)}
              countries={countries}
              includePassword={false}
              user={user}
            />
          </div>
        </div>
      </div>
    ) : null
  }
}

const mapStateToProps = createStructuredSelector({
  params: createStructuredSelector({
    partialToken: qsPartialTokenSelector,
    backend:      qsBackendSelector,
    errors:       qsErrorCodeSelector
  }),
  countries: queries.users.countriesSelector
})

const mapPropsToConfig = () => [queries.users.countriesQuery()]

const registerDetails = (
  profile: PartialProfile,
  legalAddress: LegalAddress,
  partialToken: string,
  backend
) =>
  mutateAsync(
    // $FlowFixMe
    auth.registerComplianceMutation(
      profile,
      legalAddress,
      partialToken,
      backend
    )
  )

const mapDispatchToProps = {
  registerDetails
}

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  // $FlowFixMe
  connectRequest(mapPropsToConfig)
)(RegisterRetryCompliancePage)
