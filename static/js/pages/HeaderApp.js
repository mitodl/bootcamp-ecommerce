// @flow
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"

import SiteNavbar from "../components/SiteNavbar"
import NotificationContainer from "../components/NotificationContainer"
import { addUserNotification } from "../actions"
import {
  ALERT_TYPE_TEXT,
  CMS_NOTIFICATION_SELECTOR,
  CMS_SITE_WIDE_NOTIFICATION,
  CMS_NOTIFICATION_LCL_STORAGE_ID,
  CMS_NOTIFICATION_ID_ATTR
} from "../constants"

export class HeaderApp extends React.Component<*, *> {
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
    return (
      <React.Fragment>
        <SiteNavbar />
        <NotificationContainer />
      </React.Fragment>
    )
  }
}

const mapDispatchToProps = {
  addUserNotification
}

export default compose(connect(null, mapDispatchToProps))(HeaderApp)
