// @flow
import React from "react";
import { Switch, Route } from "react-router-dom";

import { routes } from "../../lib/urls";

import ApplicationDashboardPage from "./ApplicationDashboardPage";
import PaymentHistoryPage from "./PaymentHistoryPage";

const ApplicationPages = () => (
  <React.Fragment>
    <Switch>
      <Route
        exact
        path={routes.applications.dashboard}
        component={ApplicationDashboardPage}
      />
      <Route
        exact
        path={routes.applications.paymentHistory.self}
        component={PaymentHistoryPage}
      />
    </Switch>
  </React.Fragment>
);

export default ApplicationPages;
