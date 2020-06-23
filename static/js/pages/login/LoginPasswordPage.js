// @flow
/* global SETTINGS: false */
import React from "react"
import { LOGIN_PASSWORD_PAGE_TITLE } from "../../constants"
import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync, requestAsync } from "redux-query"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import auth, { authSelector } from "../../lib/queries/auth"
import users from "../../lib/queries/users"
import { routes } from "../../lib/urls"
import { STATE_ERROR, handleAuthResponse } from "../../lib/auth"
import { formatTitle } from "../../util/util"
import { removeUserNotification } from "../../actions"

import LoginPasswordForm from "../../components/forms/LoginPasswordForm"

import type { RouterHistory, Location } from "react-router"
import type {
  AuthResponse,
  User,
  PasswordFormValues,
  HttpAuthResponse
} from "../../flow/authTypes"

type Props = {
  location: Location,
  history: RouterHistory,
  auth: AuthResponse,
  loginPassword: (
    password: string,
    partialToken: string
  ) => Promise<HttpAuthResponse<AuthResponse>>,
  getCurrentUser: () => Promise<HttpAuthResponse<User>>,
  removeUserNotification: Function
}

export class LoginPasswordPage extends React.Component<Props> {
  componentDidMount() {
    const { history, auth } = this.props

    if (!auth || !auth.partial_token) {
      // if there's no partialToken in the state
      // this page was navigated to directly and login needs to be started over
      history.push(routes.login.begin)
    }
  }

  componentWillUnmount() {
    const { removeUserNotification } = this.props
    removeUserNotification("account-exists")
  }

  async onSubmit(
    { password }: PasswordFormValues,
    { setSubmitting, setErrors }: any
  ) {
    /* eslint-disable camelcase */
    const {
      loginPassword,
      history,
      auth: { partial_token }
    } = this.props

    if (!partial_token) {
      throw Error("Invalid state: password page with no partialToken")
    }

    try {
      const { body } = await loginPassword(password, partial_token)

      handleAuthResponse(history, body, {
        [STATE_ERROR]: ({ field_errors }: AuthResponse) =>
          setErrors(field_errors)
      })
    } finally {
      setSubmitting(false)
    }
    /* eslint-enable camelcase */
  }

  render() {
    const { auth } = this.props

    if (!auth) {
      return (
        <div>
          <MetaTags>
            <title>{formatTitle(LOGIN_PASSWORD_PAGE_TITLE)}</title>
          </MetaTags>
        </div>
      )
    }

    const name = auth.extra_data.name

    return (
      <div className="container auth-page">
        <MetaTags>
          <title>{formatTitle(LOGIN_PASSWORD_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="row auth-header">
          <h1 className="col-12">Sign in</h1>
        </div>
        <div className="row auth-card card-shadow bootcamp-form">
          {name && (
            <div className="col-12">
              <p>Logging in as {name}</p>
            </div>
          )}
          <div className="col-12">
            <LoginPasswordForm onSubmit={this.onSubmit.bind(this)} />
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  auth: authSelector
})

const loginPassword = (password: string, partialToken: string) =>
  // $FlowFixMe
  mutateAsync(auth.loginPasswordMutation(password, partialToken))

const getCurrentUser = () =>
  requestAsync({
    ...users.currentUserQuery(),
    force: true
  })

const mapDispatchToProps = {
  loginPassword,
  getCurrentUser,
  removeUserNotification
}

export default compose(connect(mapStateToProps, mapDispatchToProps))(
  LoginPasswordPage
)
