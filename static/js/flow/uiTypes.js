import {ALERT_TYPE_TEXT} from "../constants"

export type NotificationProps = {
  dismiss: Function
}

export type TextNotificationProps = {
  text: string|React$Element<*>,
  persistedId?: string
}

export type ErrorNotificationProps = {
  text: string|React$Element<*>
}

export type NotificationPropTypes = TextNotificationProps | ErrorNotificationProps

export type UserNotificationSpec = {
  type: ALERT_TYPE_TEXT,
  color?: string,
  props: NotificationPropTypes
}

export type UserNotificationMapping = { [string]: UserNotificationSpec }
