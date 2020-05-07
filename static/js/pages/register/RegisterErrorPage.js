// @flow
/* global SETTINGS:false */
import React from "react"
import { MetaTags } from "react-meta-tags"

import { REGISTER_ERROR_PAGE_TITLE } from "../../constants"
import { formatTitle } from "../../util/util"

const RegisterErrorPage = () => (
  <div className="container auth-page">
    <MetaTags>
      <title>{formatTitle(REGISTER_ERROR_PAGE_TITLE)}</title>
    </MetaTags>
    <div className="auth-card card-shadow row">
      <div className="col-12">
        <div className="register-error-icon" />
        <p>Sorry, we cannot create an account for you at this time.</p>
        <p>
          Please try again later or contact us at{" "}
          <a href={`mailto:${SETTINGS.support_email}`}>
            {SETTINGS.support_email}
          </a>
        </p>
      </div>
    </div>
  </div>
)

export default RegisterErrorPage
