// @flow
import moment from "moment"
import { assert } from "chai"

import {
  setSelectedBootcampRunKey,
  setPaymentAmount,
  setInitialTime,
  setTimeoutActive,
  setToastMessage,
  showDialog,
  hideDialog,
  addUserNotification,
  removeUserNotification
} from "../actions"
import { createAssertReducerResultState } from "../util/test_utils"
import configureStore from "../store/configureStore"
import { ALERT_TYPE_TEXT } from "../constants"

describe("ui reducers", () => {
  let store, assertReducerResultState
  beforeEach(() => {
    store = configureStore()
    assertReducerResultState = createAssertReducerResultState(
      store,
      state => state.ui
    )
  })

  it("should set the payment amount", () => {
    assertReducerResultState(setPaymentAmount, ui => ui.paymentAmount, "")
  })

  it("should set the selected bootcamp run key", () => {
    assertReducerResultState(
      setSelectedBootcampRunKey,
      ui => ui.selectedBootcampRunKey,
      undefined
    )
  })

  it("should let you set the initial time, and the default is a valid time", () => {
    const initialTime = store.getState().ui.initialTime
    assert.isTrue(moment(initialTime).isValid())

    assertReducerResultState(setInitialTime, ui => ui.initialTime, initialTime)
  })

  it("should set timeoutActive", () => {
    assertReducerResultState(setTimeoutActive, ui => ui.timeoutActive, false)
  })

  it("should set the toast message", () => {
    assertReducerResultState(setToastMessage, ui => ui.toastMessage, null)
  })

  it("should set the dialog state", () => {
    store.dispatch(showDialog("dialog"))
    assert.equal(store.getState().ui.dialogVisibility["dialog"], true)
  })

  it("should unset the dialog state", () => {
    store.dispatch(hideDialog("dialog"))
    assert.equal(store.getState().ui.dialogVisibility["dialog"], false)
  })

  it("should let you add and remove user notifications", () => {
    const messageId = "some-text-alert"
    const payload = {
      [messageId]: {
        type:  ALERT_TYPE_TEXT,
        props: {
          text: "some message"
        }
      }
    }

    store.dispatch(addUserNotification(payload))
    assert.deepEqual(store.getState().ui.userNotifications, payload)

    store.dispatch(removeUserNotification(messageId))
    assert.deepEqual(store.getState().ui.userNotifications, {})
  })
})
