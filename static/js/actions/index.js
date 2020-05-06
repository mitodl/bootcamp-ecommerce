// @flow
import { createAction } from "redux-actions"

export const CLEAR_UI = "CLEAR_UI"
export const clearUI = createAction(CLEAR_UI)

export const SET_PAYMENT_AMOUNT = "SET_PAYMENT_AMOUNT"
export const setPaymentAmount = createAction(SET_PAYMENT_AMOUNT)

export const SET_SELECTED_BOOTCAMP_RUN_KEY = "SET_SELECTED_BOOTCAMP_RUN_KEY"
export const setSelectedBootcampRunKey = createAction(
  SET_SELECTED_BOOTCAMP_RUN_KEY
)

export const SET_INITIAL_TIME = "SET_INITIAL_TIME"
export const setInitialTime = createAction(SET_INITIAL_TIME)

export const SET_TIMEOUT_ACTIVE = "SET_TIMEOUT_ACTIVE"
export const setTimeoutActive = createAction(SET_TIMEOUT_ACTIVE)

export const SET_TOAST_MESSAGE = "SET_TOAST_MESSAGE"
export const setToastMessage = createAction(SET_TOAST_MESSAGE)

export const SHOW_DIALOG = "SHOW_DIALOG"
export const showDialog = createAction(SHOW_DIALOG)

export const HIDE_DIALOG = "HIDE_DIALOG"
export const hideDialog = createAction(HIDE_DIALOG)
