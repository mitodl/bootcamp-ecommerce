// @flow
/* global SETTINGS: false */
import React from "react"
import { REGISTER_EXTRA_DETAILS_PAGE_TITLE } from "../../constants"
import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync, requestAsync } from "redux-query"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import { STATE_ERROR, handleAuthResponse } from "../../lib/auth"
import auth from "../../lib/queries/auth"
import users from "../../lib/queries/users"
import { qsBackendSelector, qsPartialTokenSelector } from "../../lib/selectors"
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
  params: { partialToken: string, backend: string }
|}

type DispatchProps = {|
  registerExtraDetails: (
    profileData: ProfileForm,
    partialToken: string,
    backend?: string
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
      params: { partialToken, backend }
    } = this.props

    try {
      const { body } = await registerExtraDetails(
        profileData,
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

  render() {
    return (
      <div className="container auth-page registration-page">
        <MetaTags>
          <title>{formatTitle(REGISTER_EXTRA_DETAILS_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="row auth-header">
          <h1 className="col-12">Create Account</h1>
        </div>
        <div className="bootcamp-form auth-card card-shadow row">
          <div className="col-12 auth-step">Steps 2 of 2</div>
          <div className="col-12">
            <RegisterExtraDetailsForm onSubmit={this.onSubmit.bind(this)} />
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
  })
})

const registerExtraDetails = (
  profileData: ProfileForm,
  partialToken: string,
  backend: string
) =>
  mutateAsync(
    // $FlowFixMe
    auth.registerExtraDetailsMutation(profileData, partialToken, backend)
  )

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
