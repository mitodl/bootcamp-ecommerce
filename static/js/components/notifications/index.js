// @flow
/* global SETTINGS: false */
import React from "react"

import {
  ALERT_TYPE_ERROR,
  ALERT_TYPE_SUCCESS,
  ALERT_TYPE_TEXT
} from "../../constants"

import type {
  NotificationProps,
  TextNotificationProps,
  ErrorNotificationProps
} from "../../flow/uiTypes"

export const TextNotification = (
  props: TextNotificationProps & NotificationProps
): string | React$Element<*> => props.text

export const ErrorNotification = (
  props: ErrorNotificationProps & NotificationProps
): string | React$Element<*> =>
  props.text || (
    <span>
      Something went wrong. Please refresh the page and try again, or{" "}
      <a href={SETTINGS.support_url} target="_blank" rel="noopener noreferrer">
        contact support
      </a>{" "}
      if the problem persists.
    </span>
  )

type NotificationConfig = {
  [string]: {
    bodyComponent: (props: any) => string | React$Element<*>,
    alertProps: Object
  }
}

export const notificationConfigMap: NotificationConfig = {
  [ALERT_TYPE_TEXT]: {
    bodyComponent: TextNotification,
    alertProps:    {}
  },
  [ALERT_TYPE_ERROR]: {
    bodyComponent: ErrorNotification,
    alertProps:    {
      color: "danger"
    }
  },
  [ALERT_TYPE_SUCCESS]: {
    bodyComponent: TextNotification,
    alertProps:    {
      color: "success"
    }
  }
}
