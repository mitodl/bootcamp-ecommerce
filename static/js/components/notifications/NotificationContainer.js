// @flow
import React from "react"
import { connect } from "react-redux"
import { compose } from "redux"
import { partial } from "ramda"
import { Alert } from "reactstrap"
import wait from "waait"

import { notificationConfigMap } from "."
import { removeUserNotification } from "../../actions"
import { newSetWith, newSetWithout } from "../../util/util"
import {
  ALERT_TYPES,
  CMS_NOTIFICATION_LCL_STORAGE_ID,
  CMS_SITE_WIDE_NOTIFICATION
} from "../../constants"

import type { UserNotificationMapping } from "../../flow/uiTypes"

const DEFAULT_REMOVE_DELAY_MS = 1000

type Props = {
  userNotifications: UserNotificationMapping,
  removeUserNotification: Function,
  messageRemoveDelayMs?: number,
  alertTypes?: Array<string>
}

type State = {
  hiddenNotifications: Set<string>
}

export class NotificationContainer extends React.Component<Props, State> {
  state = {
    hiddenNotifications: new Set()
  }

  onDismiss = async (notificationKey: string) => {
    const { removeUserNotification, messageRemoveDelayMs } = this.props
    const { hiddenNotifications } = this.state

    // If the notification came from the CMS, set a local storage value to
    // avoid showing again.
    if (notificationKey === CMS_SITE_WIDE_NOTIFICATION) {
      const { userNotifications } = this.props
      const notification = userNotifications[notificationKey]
      const notificationId = notification.props.persistedId
      if (notificationId) {
        window.localStorage.setItem(
          CMS_NOTIFICATION_LCL_STORAGE_ID,
          notificationId
        )
      }
    }

    // This sets the given message in the local state to be considered hidden, then
    // removes the message from the global state and the local hidden state after a delay.
    // The message could be simply removed from the global state to get rid of it, but the
    // local state and the delay gives the Alert a chance to animate the message out.
    this.setState({
      hiddenNotifications: newSetWith(hiddenNotifications, notificationKey)
    })
    await wait(messageRemoveDelayMs || DEFAULT_REMOVE_DELAY_MS)
    removeUserNotification(notificationKey)
    this.setState({
      hiddenNotifications: newSetWithout(hiddenNotifications, notificationKey)
    })
  }

  render() {
    const { userNotifications } = this.props
    const { hiddenNotifications } = this.state
    const alertTypes = this.props.alertTypes || ALERT_TYPES

    return (
      <div className="notifications">
        {Object.entries(userNotifications || {})
          // $FlowFixMe: has trouble with Object.entries
          .filter(([, notification]) => alertTypes.includes(notification.type))
          .map(([notificationKey, notificationValue], i) => {
            // Make flow ignore notification type since flow is confused by Object.entries
            const notification: any = notificationValue
            const dismiss = partial(this.onDismiss, [notificationKey])
            const notificationConfig = notificationConfigMap[notification.type]
            const AlertBodyComponent = notificationConfig.bodyComponent
            const alertProps = notificationConfig.alertProps

            return (
              <Alert
                key={i}
                color={notification.color || "info"}
                className="rounded-0 border-0"
                isOpen={!hiddenNotifications.has(notificationKey)}
                toggle={dismiss}
                fade={true}
                {...alertProps}
              >
                <AlertBodyComponent dismiss={dismiss} {...notification.props} />
              </Alert>
            )
          })}
      </div>
    )
  }
}

const mapStateToProps = (state, ownProps) => ({
  userNotifications: state.ui.userNotifications,
  ...ownProps
})

export default compose(connect(mapStateToProps, { removeUserNotification }))(
  NotificationContainer
)
