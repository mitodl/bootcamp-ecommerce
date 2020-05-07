// @flow
/* global SETTINGS: false */
import React from "react"
import { REGISTER_DETAILS_PAGE_TITLE } from "../../constants"
import { compose } from "redux"
import { connect } from "react-redux"
import { Link } from "react-router-dom"
import { mutateAsync, requestAsync } from "redux-query"
import { connectRequest } from "redux-query-react"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import auth from "../../lib/queries/auth"
import users from "../../lib/queries/users"
import { routes } from "../../lib/urls"
import { STATE_ERROR, handleAuthResponse } from "../../lib/auth"
import queries from "../../lib/queries"
import { qsBackendSelector, qsPartialTokenSelector } from "../../lib/selectors"
import { formatTitle } from "../../util/util"

import RegisterDetailsForm from "../../components/forms/RegisterDetailsForm"

import type { RouterHistory, Location } from "react-router"

import type {
  AuthResponse,
  LegalAddress,
  User,
  Country,
  HttpAuthResponse,
  PartialProfile
} from "../../flow/authTypes"

type RegisterProps = {|
  location: Location,
  history: RouterHistory,
  params: { partialToken: string, backend: string }
|}

type StateProps = {|
  countries: Array<Country>
|}

type DispatchProps = {|
  registerDetails: (
    name: string,
    password: string,
    legalAddress: LegalAddress,
    partialToken: string,
    backend: string
  ) => Promise<HttpAuthResponse<AuthResponse>>,
  getCurrentUser: () => Promise<HttpAuthResponse<User>>
|}

type Props = {|
  ...RegisterProps,
  ...StateProps,
  ...DispatchProps
|}

export class RegisterDetailsPage extends React.Component<Props> {
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
        detailsData.password,
        detailsData.legal_address,
        partialToken,
        backend
      )

      handleAuthResponse(
        history,
        body,
        {
          // eslint-disable-next-line camelcase
          [STATE_ERROR]: ({ field_errors }: AuthResponse) =>
            setErrors(field_errors)
        },
        backend
      )
    } finally {
      setSubmitting(false)
    }
  }

  render() {
    const { countries } = this.props

    return (
      <div className="container auth-page registration-page">
        <MetaTags>
          <title>{formatTitle(REGISTER_DETAILS_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="auth-header row d-flex flex-row align-items-center justify-content-between flex-nowrap">
          <div className="col-auto flex-shrink-1">
            <h1>Create an Account</h1>
          </div>
          <div className="col-auto align-text-right gray-text">
            <h4>Step 1 of 2</h4>
          </div>
        </div>
        <div className="auth-card card-shadow row">
          <div className="container">
            <div className="row">
              <div className="col-12 form-group">
                {`Already have an account? `}
                <Link to={routes.login.begin}>Click here</Link>
              </div>
            </div>
            <div className="row">
              <div className="col-12 auth-form">
                <RegisterDetailsForm
                  onSubmit={this.onSubmit.bind(this)}
                  countries={countries}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  params: createStructuredSelector({
    partialToken: qsPartialTokenSelector,
    backend:      qsBackendSelector
  }),
  countries: queries.users.countriesSelector
})

const mapPropsToConfig = () => [queries.users.countriesQuery()]

const registerDetails = (
  profile: PartialProfile,
  password: string,
  legalAddress: LegalAddress,
  partialToken: string,
  backend
) =>
  mutateAsync(
    // $FlowFixMe
    auth.registerDetailsMutation(
      profile,
      password,
      legalAddress,
      partialToken,
      backend
    )
  )

const getCurrentUser = () =>
  requestAsync({
    ...users.currentUserQuery(),
    force: true
  })

const mapDispatchToProps = {
  registerDetails,
  getCurrentUser
}

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  // $FlowFixMe
  connectRequest(mapPropsToConfig)
)(RegisterDetailsPage)
