// @flow
import React from "react"

import { ALERT_TYPE_TEXT } from "../../constants"

import type { TextNotificationProps } from "../../reducers/ui"

type ComponentProps = {
  dismiss: Function
}

export const TextNotification = (
  props: TextNotificationProps & ComponentProps
) => <span>{props.text}</span>

export const notificationTypeMap = {
  [ALERT_TYPE_TEXT]: TextNotification
}
