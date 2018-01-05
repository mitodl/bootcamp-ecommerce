// @flow
import { combineReducers } from "redux"
import moment from "moment"

import {
  CLEAR_UI,
  SET_SELECTED_KLASS_KEY,
  SET_PAYMENT_AMOUNT,
  SET_INITIAL_TIME,
  SET_TIMEOUT_ACTIVE,
  SET_TOAST_MESSAGE
} from "../actions"
import type { Action } from "../flow/reduxTypes"
import { reducers as restReducers } from "../rest"

export type ToastMessage = {
  message: string,
  title?: string,
  icon?: string
}

export type UIState = {
  paymentAmount: string,
  selectedKlassKey?: number,
  initialTime: string,
  timeoutActive: boolean,
  toastMessage: ?ToastMessage
}
const INITIAL_UI_STATE = {
  paymentAmount: "",
  initialTime:   moment().toISOString(),
  timeoutActive: false,
  toastMessage:  null
}

export const ui = (state: UIState = INITIAL_UI_STATE, action: Action) => {
  switch (action.type) {
  case CLEAR_UI:
    return INITIAL_UI_STATE
  case SET_PAYMENT_AMOUNT:
    return { ...state, paymentAmount: action.payload }
  case SET_SELECTED_KLASS_KEY:
    return { ...state, selectedKlassKey: action.payload }
  case SET_INITIAL_TIME:
    return { ...state, initialTime: action.payload }
  case SET_TIMEOUT_ACTIVE:
    return { ...state, timeoutActive: action.payload }
  case SET_TOAST_MESSAGE:
    return { ...state, toastMessage: action.payload }
  default:
    return state
  }
}

export default combineReducers({
  ui,
  ...restReducers
})
