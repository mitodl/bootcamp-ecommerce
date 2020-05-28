// @flow
import React from "react"
import { Switch, Route } from "react-router-dom"

import { routes } from "../../lib/urls"

import ApplicationDashboardPage from "./ApplicationDashboardPage"

const ApplicationPages = () => (
  <React.Fragment>
    <Switch>
      <Route
        exact
        path={routes.applications.dashboard}
        component={ApplicationDashboardPage}
      />
    </Switch>
  </React.Fragment>
)

export default ApplicationPages
