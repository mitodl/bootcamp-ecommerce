// @flow
import React from "react"
import { connect } from "react-redux"
import { compose } from "redux"
import { partial } from "ramda"
import { Alert } from "reactstrap"

import { removeUserNotification } from "../actions"
import { newSetWith, newSetWithout, timeoutPromise } from "../util/util"
import { notificationTypeMap } from "./notifications"
import { CMS_SITE_WIDE_NOTIFICATION } from "../constants"

import type { UserNotificationMapping } from "../reducers/ui"

const DEFAULT_REMOVE_DELAY_MS = 1000

type Props = {
  userNotifications: UserNotificationMapping,
  removeUserNotification: Function,
  messageRemoveDelayMs?: number
}

type State = {
  hiddenNotifications: Set<string>
}

export class NotificationContainer extends React.Component<Props, State> {
  state = {
    hiddenNotifications: new Set()
  }

  onDismiss = (notificationKey: string) => {
    const { removeUserNotification, messageRemoveDelayMs } = this.props
    const { hiddenNotifications } = this.state

    // If the notification came from the CMS, set a local storage value to
    // avoid showing again.
    if (notificationKey === CMS_SITE_WIDE_NOTIFICATION) {
      const { userNotifications } = this.props
      const notification = userNotifications[notificationKey]
      const notificationId = notification.props.persistedId
      if (notificationId) {
        window.localStorage.setItem("dismissedNotification", notificationId)
      }
    }

    // This sets the given message in the local state to be considered hidden, then
    // removes the message from the global state and the local hidden state after a delay.
    // The message could be simply removed from the global state to get rid of it, but the
    // local state and the delay gives the Alert a chance to animate the message out.
    this.setState({
      hiddenNotifications: newSetWith(hiddenNotifications, notificationKey)
    })
    return timeoutPromise(() => {
      removeUserNotification(notificationKey)
      this.setState({
        hiddenNotifications: newSetWithout(hiddenNotifications, notificationKey)
      })
    }, messageRemoveDelayMs || DEFAULT_REMOVE_DELAY_MS)
  }

  render() {
    const { userNotifications } = this.props
    const { hiddenNotifications } = this.state

    return (
      <div className="notifications">
        {Object.keys(userNotifications).map((notificationKey, i) => {
          const dismiss = partial(this.onDismiss, [notificationKey])
          const notification = userNotifications[notificationKey]
          const AlertBodyComponent = notificationTypeMap[notification.type]

          return (
            <Alert
              key={i}
              color={notification.color || "info"}
              className="rounded-0 border-0"
              isOpen={!hiddenNotifications.has(notificationKey)}
              toggle={dismiss}
              fade={true}
            >
              <AlertBodyComponent dismiss={dismiss} {...notification.props} />
            </Alert>
          )
        })}
      </div>
    )
  }
}

const mapStateToProps = state => ({
  userNotifications: state.ui.userNotifications
})

export default compose(connect(mapStateToProps, { removeUserNotification }))(
  NotificationContainer
)
