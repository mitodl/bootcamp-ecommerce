// @flow
/* global SETTINGS: false */
import React from "react"
import { connect } from "react-redux"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import { REGISTER_CONFIRM_PAGE_TITLE } from "../../constants"
import { routes } from "../../lib/urls"
import { qsEmailSelector } from "../../lib/selectors"
import { formatTitle } from "../../util/util"

type Props = {|
  params: { email: ?string }
|}

export class RegisterConfirmSentPage extends React.Component<Props> {
  render() {
    const {
      params: { email }
    } = this.props

    return (
      <div className="container auth-page registration-page">
        <MetaTags>
          <title>{formatTitle(REGISTER_CONFIRM_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="row auth-header">
          <div className="col-12">
            <h1>Sign Up</h1>
          </div>
        </div>
        <div className="row auth-card">
          <div className="col-12">
            <h2 className="font-weight-600">Thank You!</h2>
            <p>
              We sent an email to <span className="email">{email}</span>
              ,<br /> please verify your address to continue.
            </p>
            <p>
              If you do NOT receive your verification email, here’s what to do:
            </p>
            <ol>
              <li>
                <span className="font-weight-600">Wait a few moments.</span> It
                might take several minutes to receive your verification email.
              </li>
              <li>
                <span className="font-weight-600">Check your spam folder.</span>{" "}
                It might be there.
              </li>
              <li>
                <span className="font-weight-600">Is your email correct?</span>{" "}
                If you made a typo, no problem, just try{" "}
                <a href={routes.register.begin}>creating an account</a> again.
              </li>
            </ol>
            <div className="contact-support">
              <span className="font-weight-600">
                Still no verification email?
              </span>{" "}
              Please contact our
              <a
                href={SETTINGS.support_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {` MIT Bootcamp Customer Support Center`}.
              </a>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  params: createStructuredSelector({ email: qsEmailSelector })
})

export default connect(mapStateToProps)(RegisterConfirmSentPage)
