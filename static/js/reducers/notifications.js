// @flow
import { mergeRight, omit } from "ramda"

import { ADD_USER_NOTIFICATION, REMOVE_USER_NOTIFICATION } from "../actions"
import { ALERT_TYPE_TEXT } from "../constants"

import type { Action } from "../flow/reduxTypes"

export type TextNotificationProps = { text: string }

export type UserNotificationSpec = {
  type: ALERT_TYPE_TEXT,
  color: string,
  props: TextNotificationProps
}

export type UserNotificationMapping = { [string]: UserNotificationSpec }

export type NotificationState = UserNotificationMapping

export const INITIAL_NOTIFICATION_STATE: NotificationState = {}

export const userNotifications = (
  state: NotificationState = INITIAL_NOTIFICATION_STATE,
  action: Action<any, null>
): NotificationState => {
  switch (action.type) {
  case ADD_USER_NOTIFICATION:
    return mergeRight(state, action.payload)
  case REMOVE_USER_NOTIFICATION:
    return omit([action.payload], state)
  }
  return state
}

export default userNotifications
