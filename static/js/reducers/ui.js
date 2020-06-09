// @flow
import moment from "moment"

import {
  CLEAR_UI,
  SET_SELECTED_BOOTCAMP_RUN_KEY,
  SET_PAYMENT_AMOUNT,
  SET_INITIAL_TIME,
  SET_TIMEOUT_ACTIVE,
  SET_TOAST_MESSAGE,
  SHOW_DIALOG,
  HIDE_DIALOG,
  ADD_USER_NOTIFICATION,
  REMOVE_USER_NOTIFICATION
} from "../actions"

import type { Action } from "../flow/reduxTypes"
import { mergeRight, omit } from "ramda"
import { ALERT_TYPE_TEXT } from "../constants"

export type ToastMessage = {
  message: string,
  title?: string,
  icon?: string
}

export type UIState = {
  paymentAmount: string,
  selectedBootcampRunKey?: number,
  initialTime: string,
  timeoutActive: boolean,
  toastMessage: ?ToastMessage,
  dialogVisibility: Object,
  userNotifications: Object
}
const INITIAL_UI_STATE = {
  paymentAmount:     "",
  initialTime:       moment().toISOString(),
  timeoutActive:     false,
  toastMessage:      null,
  dialogVisibility:  {},
  userNotifications: {}
}

export type TextNotificationProps = {
  text: string,
  persistedId?: string
}

export type UserNotificationSpec = {
  type: ALERT_TYPE_TEXT,
  color: string,
  props: TextNotificationProps
}

export type UserNotificationMapping = { [string]: UserNotificationSpec }

const ui = (state: UIState = INITIAL_UI_STATE, action: Action) => {
  switch (action.type) {
  case CLEAR_UI:
    return INITIAL_UI_STATE
  case SET_PAYMENT_AMOUNT:
    return { ...state, paymentAmount: action.payload }
  case SET_SELECTED_BOOTCAMP_RUN_KEY:
    return { ...state, selectedBootcampRunKey: action.payload }
  case SET_INITIAL_TIME:
    return { ...state, initialTime: action.payload }
  case SET_TIMEOUT_ACTIVE:
    return { ...state, timeoutActive: action.payload }
  case SET_TOAST_MESSAGE:
    return { ...state, toastMessage: action.payload }
  case SHOW_DIALOG:
    return {
      ...state,
      dialogVisibility: {
        ...state.dialogVisibility,
        [action.payload]: true
      }
    }
  case HIDE_DIALOG:
    return {
      ...state,
      dialogVisibility: {
        ...state.dialogVisibility,
        [action.payload]: false
      }
    }
  case ADD_USER_NOTIFICATION:
    return {
      ...state,
      userNotifications: mergeRight(state.userNotifications, action.payload)
    }
  case REMOVE_USER_NOTIFICATION:
    return {
      ...state,
      userNotifications: omit([action.payload], state.userNotifications)
    }
  default:
    return state
  }
}

export default ui
