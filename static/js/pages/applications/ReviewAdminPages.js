// @flow
import React from "react";
import { Route } from "react-router-dom";

import { routes } from "../../lib/urls";

import ReviewDetailPage from "./ReviewDetailPage";
import ReviewDashboardPage from "./ReviewDashboardPage";

export default function ReviewAdminPages() {
  return (
    <>
      <Route
        exact
        path={routes.review.dashboard}
        component={ReviewDashboardPage}
      />
      <Route exact path={routes.review.detail} component={ReviewDetailPage} />
    </>
  );
}
