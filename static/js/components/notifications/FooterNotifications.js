// @flow
import React from "react"
import NotificationContainer from "./NotificationContainer"
import { ALERT_TYPE_ERROR, ALERT_TYPE_SUCCESS } from "../../constants"

const FooterNotifications = () => (
  <NotificationContainer alertTypes={[ALERT_TYPE_SUCCESS, ALERT_TYPE_ERROR]} />
)

export default FooterNotifications
