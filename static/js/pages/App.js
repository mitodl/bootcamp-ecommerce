// @flow
import React from "react"

import { Switch, Route } from "react-router"
import urljoin from "url-join"

import { routes } from "../lib/urls"

import PrivateRoute from "../components/PrivateRoute"
import ProfilePages from "./profile/ProfilePages"
import LoginPages from "./login/LoginPages"
import RegisterPages from "./register/RegisterPages"
import PaymentPage from "./PaymentPage"
import EmailConfirmPage from "./settings/EmailConfirmPage"
import AccountSettingsPage from "./settings/AccountSettingsPage"

import { compose } from "redux"
import { connect } from "react-redux"
import { createStructuredSelector } from "reselect"
import users, { currentUserSelector } from "../lib/queries/users"
import { connectRequest } from "redux-query-react"

import type { Match } from "react-router"
import type { Store } from "redux"
import type { CurrentUser } from "../flow/authTypes"

type Props = {
  match: Match,
  currentUser: ?CurrentUser,
  store: Store<*, *>
}

export class App extends React.Component<Props, void> {
  render() {
    const { match, currentUser } = this.props
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
        </Switch>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  currentUser: currentUserSelector
})

const mapPropsToConfig = () => [users.currentUserQuery()]

export default compose(
  connect(mapStateToProps),
  connectRequest(mapPropsToConfig)
)(App)
