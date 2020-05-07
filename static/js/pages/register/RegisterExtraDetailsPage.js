// @flow
/* global SETTINGS: false */
import React from "react"
import { REGISTER_EXTRA_DETAILS_PAGE_TITLE } from "../../constants"
import { compose } from "redux"
import { connect } from "react-redux"
import { Link } from "react-router-dom"
import { mutateAsync, requestAsync } from "redux-query"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import { STATE_ERROR, handleAuthResponse } from "../../lib/auth"
import auth from "../../lib/queries/auth"
import users from "../../lib/queries/users"
import { routes } from "../../lib/urls"
import { qsPartialTokenSelector } from "../../lib/selectors"
import { formatTitle } from "../../util/util"

import RegisterExtraDetailsForm from "../../components/forms/RegisterExtraDetailsForm"

import type { RouterHistory, Location } from "react-router"
import type {
  HttpAuthResponse,
  AuthResponse,
  ProfileForm,
  User
} from "../../flow/authTypes"

type RegisterProps = {|
  location: Location,
  history: RouterHistory,
  params: { partialToken: string }
|}

type DispatchProps = {|
  registerExtraDetails: (
    profileData: ProfileForm,
    partialToken: string
  ) => Promise<HttpAuthResponse<AuthResponse>>,
  getCurrentUser: () => Promise<HttpAuthResponse<User>>
|}

type Props = {|
  ...RegisterProps,
  ...DispatchProps
|}

export class RegisterExtraDetailsPage extends React.Component<Props> {
  async onSubmit(profileData: ProfileForm, { setSubmitting, setErrors }: any) {
    const {
      history,
      registerExtraDetails,
      params: { partialToken }
    } = this.props

    try {
      const { body } = await registerExtraDetails(profileData, partialToken)

      handleAuthResponse(history, body, {
        // eslint-disable-next-line camelcase
        [STATE_ERROR]: ({ field_errors }: AuthResponse) =>
          setErrors(field_errors)
      })
    } finally {
      setSubmitting(false)
    }
  }

  render() {
    return (
      <div className="container auth-page registration-page">
        <MetaTags>
          <title>{formatTitle(REGISTER_EXTRA_DETAILS_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="auth-header row d-flex flex-row align-items-center justify-content-between flex-nowrap">
          <div className="col-auto flex-shrink-1">
            <h1>Create an Account</h1>
          </div>
          <div className="col-auto align-text-right gray-text">
            <h4>Step 2 of 2</h4>
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
                <RegisterExtraDetailsForm onSubmit={this.onSubmit.bind(this)} />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  params: createStructuredSelector({ partialToken: qsPartialTokenSelector })
})

const registerExtraDetails = (profileData: ProfileForm, partialToken: string) =>
  // $FlowFixMe
  mutateAsync(auth.registerExtraDetailsMutation(profileData, partialToken))

const getCurrentUser = () =>
  requestAsync({
    ...users.currentUserQuery(),
    force: true
  })

const mapDispatchToProps = {
  registerExtraDetails: registerExtraDetails,
  getCurrentUser
}

export default compose(connect(mapStateToProps, mapDispatchToProps))(
  RegisterExtraDetailsPage
)
