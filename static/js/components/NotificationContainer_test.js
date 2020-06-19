// @flow
import { assert } from "chai"

import NotificationContainer, {
  NotificationContainer as InnerNotificationContainer
} from "./NotificationContainer"
import { TextNotification } from "./notifications"
import {
  ALERT_TYPE_TEXT,
  CMS_NOTIFICATION_LCL_STORAGE_ID,
  CMS_SITE_WIDE_NOTIFICATION
} from "../constants"
import IntegrationTestHelper from "../util/integration_test_helper"

describe("NotificationContainer component", () => {
  const messages = {
    message1: {
      type:  ALERT_TYPE_TEXT,
      props: { text: "derp" }
    },
    message2: {
      type:  ALERT_TYPE_TEXT,
      props: { text: "herp" }
    }
  }

  let helper, render

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    render = helper.configureHOCRenderer(
      NotificationContainer,
      InnerNotificationContainer,
      {
        ui: {
          userNotifications: {}
        }
      },
      {}
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("shows notifications", async () => {
    const { inner } = await render({
      ui: {
        userNotifications: messages
      }
    })
    const alerts = inner.find("Alert")
    assert.lengthOf(alerts, Object.keys(messages).length)
    assert.equal(alerts.at(0).prop("children").type, TextNotification)
    assert.equal(alerts.at(1).prop("children").type, TextNotification)
  })

  //
  ;[
    [undefined, "info"],
    ["danger", "danger"]
  ].forEach(([color, expectedColor]) => {
    it(`shows a ${expectedColor} color notification given a ${String(
      color
    )} color prop`, async () => {
      const { inner } = await render({
        ui: {
          userNotifications: {
            aMessage: {
              type:  ALERT_TYPE_TEXT,
              color: color,
              props: { text: "derp" }
            }
          }
        }
      })
      assert.equal(inner.find("Alert").prop("color"), expectedColor)
    })
  })

  it("hides a message when it's dismissed, then removes it from global state", async () => {
    const delayMs = 5
    const { inner } = await render(
      {
        ui: {
          userNotifications: messages
        }
      },
      { messageRemoveDelayMs: delayMs }
    )
    const alert = inner.find("Alert").at(0)
    alert.prop("toggle")()
    assert.deepEqual(inner.state(), {
      hiddenNotifications: new Set(["message1"])
    })
  })

  it("shows cms notification", async () => {
    const { inner } = await render({
      ui: {
        userNotifications: {
          [CMS_SITE_WIDE_NOTIFICATION]: {
            type:  ALERT_TYPE_TEXT,
            props: { text: "Cms Notification", persistedId: 1 }
          }
        }
      }
    })

    const alerts = inner.find("Alert")
    assert.lengthOf(alerts, 1)
    const cmsNotificationContent = alerts.at(0).prop("children")
    assert.equal(cmsNotificationContent.type, TextNotification)
    assert.equal(cmsNotificationContent.props.text, "Cms Notification")
    assert.isNotNull(cmsNotificationContent.props.persistedId)
    assert.equal(cmsNotificationContent.props.persistedId, 1)
    assert.isNull(window.localStorage.getItem(CMS_NOTIFICATION_LCL_STORAGE_ID))
  })

  it("removes cms notifictaion, adds it in the local storage", async () => {
    const { inner } = await render({
      ui: {
        userNotifications: {
          [CMS_SITE_WIDE_NOTIFICATION]: {
            type:  ALERT_TYPE_TEXT,
            props: { text: "Cms Notifictaion", persistedId: 1 }
          }
        }
      }
    })

    const alert = inner.find("Alert").at(0)
    alert.prop("toggle")()
    assert.deepEqual(inner.state(), {
      hiddenNotifications: new Set([CMS_SITE_WIDE_NOTIFICATION])
    })
    assert.isNotNull(
      window.localStorage.getItem(CMS_NOTIFICATION_LCL_STORAGE_ID)
    )
    assert.equal(
      window.localStorage.getItem(CMS_NOTIFICATION_LCL_STORAGE_ID),
      1
    )
  })
})
