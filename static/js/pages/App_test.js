import React from "react"
import { shallow } from "enzyme"
import { assert } from "chai"

import { App } from "./App"
import NotificationContainer from "../components/notifications/NotificationContainer"

import { makeUser } from "../factories/user"
import { ALERT_TYPE_TEXT } from "../constants"

describe("App", () => {
  it("shows only text notifications", async () => {
    const wrapper = shallow(
      <App currentUser={makeUser()} match={{ url: "/" }} />
    )
    assert.deepEqual(wrapper.find(NotificationContainer).prop("alertTypes"), [
      ALERT_TYPE_TEXT
    ])
  })
})
