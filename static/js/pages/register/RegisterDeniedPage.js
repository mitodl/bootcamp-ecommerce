// @flow
/* global SETTINGS:false */
import React from "react"
import { REGISTER_DENIED_PAGE_TITLE } from "../../constants"
import { connect } from "react-redux"
import { createStructuredSelector } from "reselect"

import { qsErrorSelector } from "../../lib/selectors"
import { MetaTags } from "react-meta-tags"
import { formatTitle } from "../../util/util"

type Props = {|
  params: { error: ?string }
|}

export class RegisterDeniedPage extends React.Component<Props> {
  render() {
    const {
      params: { error }
    } = this.props

    return (
      <div className="container auth-page">
        <MetaTags>
          <title>{formatTitle(REGISTER_DENIED_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="auth-card card-shadow row">
          <div className="col-12">
            <div className="register-error-icon" />
            <p>Sorry, we cannot create an account for you at this time.</p>
            {error ? <p className="error-detail">{error}</p> : null}
            <p>
              Please contact us at our{" "}
              <a
                href={SETTINGS.support_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Customer Support Center
              </a>
            </p>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  params: createStructuredSelector({ error: qsErrorSelector })
})

export default connect(mapStateToProps)(RegisterDeniedPage)
