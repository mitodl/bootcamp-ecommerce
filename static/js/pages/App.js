// @flow
import React from "react"
import { useSelector } from "react-redux"
import { Switch, Route } from "react-router"
import urljoin from "url-join"

import { useRequest } from "redux-query-react"

import PrivateRoute from "../components/PrivateRoute"
import ProfilePages from "./profile/ProfilePages"
import LoginPages from "./login/LoginPages"
import RegisterPages from "./register/RegisterPages"
import ApplicationPages from "./applications/ApplicationPages"
import PaymentPage from "./PaymentPage"
import EmailConfirmPage from "./settings/EmailConfirmPage"
import AccountSettingsPage from "./settings/AccountSettingsPage"

import users, { currentUserSelector } from "../lib/queries/users"
import { routes } from "../lib/urls"

import type { Match } from "react-router"

type Props = {
  match: Match
}

export default function App(props: Props) {
  const { match } = props

  const currentUser = useSelector(currentUserSelector)
  useRequest(users.currentUserQuery())

  if (!currentUser) {
    // application is still loading
    return <div className="app" />
  }

  return (
    <div className="app">
      <Switch>
        <Route path={`${match.url}pay/`} component={PaymentPage} />
        <Route
          path={urljoin(match.url, String(routes.profile))}
          component={ProfilePages}
        />
        <Route
          path={urljoin(match.url, String(routes.login))}
          component={LoginPages}
        />
        <Route
          path={urljoin(match.url, String(routes.register))}
          component={RegisterPages}
        />
        <Route
          path={urljoin(match.url, String(routes.account.confirmEmail))}
          component={EmailConfirmPage}
        />
        <PrivateRoute
          path={urljoin(match.url, String(routes.accountSettings))}
          component={AccountSettingsPage}
        />
        <PrivateRoute
          path={urljoin(match.url, String(routes.applications))}
          component={ApplicationPages}
        />
      </Switch>
    </div>
  )
}
