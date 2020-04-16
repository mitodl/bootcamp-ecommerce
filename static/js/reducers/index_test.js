import configureTestStore from "redux-asserts"
import moment from "moment"
import { assert } from "chai"

import {
  setSelectedKlassKey,
  setPaymentAmount,
  setInitialTime,
  setTimeoutActive,
  setToastMessage,
  showDialog,
  hideDialog
} from "../actions"
import rootReducer from "../reducers"
import { createAssertReducerResultState } from "../util/test_utils"

describe("reducers", () => {
  let store, assertReducerResultState
  beforeEach(() => {
    store = configureTestStore(rootReducer)
    assertReducerResultState = createAssertReducerResultState(
      store,
      state => state.ui
    )
  })

  describe("ui", () => {
    it("should set the payment amount", () => {
      assertReducerResultState(setPaymentAmount, ui => ui.paymentAmount, "")
    })

    it("should set the selected klass index", () => {
      assertReducerResultState(
        setSelectedKlassKey,
        ui => ui.selectedKlassKey,
        undefined
      )
    })

    it("should let you set the initial time, and the default is a valid time", () => {
      const initialTime = store.getState().ui.initialTime
      assert.isTrue(moment(initialTime).isValid())

      assertReducerResultState(
        setInitialTime,
        ui => ui.initialTime,
        initialTime
      )
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
  })
})
