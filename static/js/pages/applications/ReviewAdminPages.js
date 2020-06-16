// @flow
import React from "react"
import { Switch, Route } from "react-router-dom"

import { routes } from "../../lib/urls"

import { ReviewDetailPage } from "./ReviewDetailPage"

const ReviewAdminPages = () => (
  <Switch>
    <Route exact path={routes.review.detail} component={ReviewDetailPage} />
  </Switch>
)

export default ReviewAdminPages
