// @flow
/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query-react"
import { Link } from "react-router-dom"
import { mutateAsync } from "redux-query"
import { path } from "ramda"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import { addUserNotification } from "../../actions"
import { ALERT_TYPE_TEXT, REGISTER_CONFIRM_PAGE_TITLE } from "../../constants"
import queries from "../../lib/queries"
import { routes } from "../../lib/urls"
import {
  STATE_REGISTER_DETAILS,
  STATE_INVALID_EMAIL,
  handleAuthResponse
} from "../../lib/auth"

import { authSelector } from "../../lib/queries/auth"
import {
  qsVerificationCodeSelector,
  qsPartialTokenSelector
} from "../../lib/selectors"
import { formatTitle } from "../../util/util"

import type { RouterHistory, Location } from "react-router"
import type { AuthResponse } from "../../flow/authTypes"

type Props = {
  addUserNotification: Function,
  location: Location,
  history: RouterHistory,
  auth: ?AuthResponse
}

export class RegisterConfirmPage extends React.Component<Props> {
  componentDidUpdate(prevProps: Props) {
    const { addUserNotification, auth, history } = this.props
    const prevState = path(["auth", "state"], prevProps)

    if (auth && auth.state !== prevState) {
      handleAuthResponse(history, auth, {
        [STATE_REGISTER_DETAILS]: () => {
          addUserNotification({
            "email-verified": {
              type:  ALERT_TYPE_TEXT,
              props: {
                text:
                  "Success! We've verified your email. Please finish your account creation below."
              }
            }
          })
        }
      })
    }
  }

  render() {
    const { auth } = this.props

    return (
      <div className="container auth-page">
        <MetaTags>
          <title>{formatTitle(REGISTER_CONFIRM_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="row">
          <div className="col">
            {auth && auth.state === STATE_INVALID_EMAIL ? (
              <React.Fragment>
                <p>No confirmation code was provided or it has expired.</p>
                <Link to={routes.register.begin}>Click here</Link> to register
                again.
              </React.Fragment>
            ) : (
              <p>Confirming...</p>
            )}
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  auth:   authSelector,
  params: createStructuredSelector({
    verificationCode: qsVerificationCodeSelector,
    partialToken:     qsPartialTokenSelector
  })
})

const registerConfirmEmail = (code: string, partialToken: string) =>
  // $FlowFixMe
  mutateAsync(queries.auth.registerConfirmEmailMutation(code, partialToken))

const mapPropsToConfig = ({ params: { verificationCode, partialToken } }) =>
  registerConfirmEmail(verificationCode, partialToken)

const mapDispatchToProps = {
  addUserNotification
}

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  // $FlowFixMe
  connectRequest(mapPropsToConfig)
)(RegisterConfirmPage)
