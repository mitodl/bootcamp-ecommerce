// @flow
/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"
import { MetaTags } from "react-meta-tags"
import { Link } from "react-router-dom"

import auth from "../../lib/queries/auth"
import { routes, getNextParam } from "../../lib/urls"
import {
  STATE_ERROR,
  STATE_REGISTER_REQUIRED,
  handleAuthResponse
} from "../../lib/auth"
import { LOGIN_EMAIL_PAGE_TITLE } from "../../constants"
import { formatTitle } from "../../util/util"
import EmailForm from "../../components/forms/EmailForm"

import type { RouterHistory, Location } from "react-router"
import type {
  HttpAuthResponse,
  AuthResponse,
  EmailFormValues
} from "../../flow/authTypes"

type Props = {
  location: Location,
  history: RouterHistory,
  loginEmail: (
    email: string,
    next: ?string
  ) => Promise<HttpAuthResponse<AuthResponse>>
}

export class LoginEmailPage extends React.Component<Props> {
  async onSubmit(
    { email }: EmailFormValues,
    { setSubmitting, setErrors }: any
  ) {
    const { loginEmail, location, history } = this.props
    const nextUrl = getNextParam(location.search)

    try {
      const { body } = await loginEmail(email, nextUrl)

      handleAuthResponse(history, body, {
        // eslint-disable-next-line camelcase
        [STATE_ERROR]: ({ field_errors }: AuthResponse) =>
          setErrors(field_errors),
        // eslint-disable-next-line camelcase
        [STATE_REGISTER_REQUIRED]: ({ field_errors }: AuthResponse) =>
          setErrors(field_errors)
      })
    } finally {
      setSubmitting(false)
    }
  }

  render() {
    const link = `${routes.register.begin}${this.props.location.search}`

    return (
      <div className="container auth-page">
        <MetaTags>
          <title>{formatTitle(LOGIN_EMAIL_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="row auth-header">
          <h1 className="col-12">Sign in</h1>
        </div>
        <div className="row auth-card card-shadow bootcamp-form">
          <div className="col-12">
            <EmailForm onSubmit={this.onSubmit.bind(this)}>
              <React.Fragment>
                <span>Don't have an account? </span>
                <Link to={link} className="link-light-blue">
                  Create Account
                </Link>
              </React.Fragment>
            </EmailForm>
          </div>
        </div>
      </div>
    )
  }
}

const loginEmail = (email: string, nextUrl: ?string) =>
  // $FlowFixMe
  mutateAsync(auth.loginEmailMutation(email, nextUrl))

const mapDispatchToProps = {
  loginEmail
}

export default compose(connect(null, mapDispatchToProps))(LoginEmailPage)
