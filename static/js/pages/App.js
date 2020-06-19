// @flow
import React, { Component } from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query-react"
import { Switch, Route } from "react-router"
import urljoin from "url-join"
import { createStructuredSelector } from "reselect"

import PrivateRoute from "../components/PrivateRoute"
import SiteNavbar from "../components/SiteNavbar"
import NotificationContainer from "../components/NotificationContainer"
import Drawer from "../components/Drawer"
import LoginPages from "./login/LoginPages"
import RegisterPages from "./register/RegisterPages"
import ApplicationPages from "./applications/ApplicationPages"
import ReviewAdminPages from "./applications/ReviewAdminPages"

import PaymentPage from "./PaymentPage"
import EmailConfirmPage from "./settings/EmailConfirmPage"
import AccountSettingsPage from "./settings/AccountSettingsPage"

import users, { currentUserSelector } from "../lib/queries/users"
import { routes } from "../lib/urls"

import {
  ALERT_TYPE_TEXT,
  CMS_NOTIFICATION_SELECTOR,
  CMS_SITE_WIDE_NOTIFICATION,
  CMS_NOTIFICATION_LCL_STORAGE_ID,
  CMS_NOTIFICATION_ID_ATTR
} from "../constants"
import type { Match } from "react-router"

import { addUserNotification } from "../actions"

import type { CurrentUser } from "../flow/authTypes"

type Props = {
  currentUser: CurrentUser,
  match: Match,
  addUserNotification: Function
}

export class App extends Component<Props> {
  componentDidMount() {
    const { addUserNotification } = this.props
    const cmsNotification = document.querySelector(CMS_NOTIFICATION_SELECTOR)
    if (cmsNotification) {
      const notificationId = cmsNotification.getAttribute(
        CMS_NOTIFICATION_ID_ATTR
      )
      const notificationMessage = cmsNotification.textContent
      if (
        window.localStorage.getItem(CMS_NOTIFICATION_LCL_STORAGE_ID) !==
        notificationId
      ) {
        addUserNotification({
          [CMS_SITE_WIDE_NOTIFICATION]: {
            type:  ALERT_TYPE_TEXT,
            props: {
              text:        notificationMessage,
              persistedId: notificationId
            }
          }
        })
      }
    }
  }

  render() {
    const { match, currentUser } = this.props

    if (!currentUser) {
      // application is still loading
      return <div className="app" />
    }

    return (
      <div className="app">
        <SiteNavbar />
        <NotificationContainer />
        <div className="body-content">
          <Switch>
            <Route path={`${match.url}pay/`} component={PaymentPage} />
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
            <PrivateRoute
              path={urljoin(match.url, String(routes.review))}
              component={ReviewAdminPages}
            />
          </Switch>
        </div>
        <Drawer />
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  currentUser: currentUserSelector
})

const mapDispatchToProps = {
  addUserNotification
}

const mapPropsToConfigs = () => [users.currentUserQuery()]

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(App)
