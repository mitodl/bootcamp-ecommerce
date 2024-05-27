// @flow
import { createAction } from "redux-actions";

export const CLEAR_UI = "CLEAR_UI";
export const clearUI = createAction(CLEAR_UI);

export const SET_PAYMENT_AMOUNT = "SET_PAYMENT_AMOUNT";
export const setPaymentAmount = createAction(SET_PAYMENT_AMOUNT);

export const SET_SELECTED_BOOTCAMP_RUN_KEY = "SET_SELECTED_BOOTCAMP_RUN_KEY";
export const setSelectedBootcampRunKey = createAction(
  SET_SELECTED_BOOTCAMP_RUN_KEY,
);

export const SET_INITIAL_TIME = "SET_INITIAL_TIME";
export const setInitialTime = createAction(SET_INITIAL_TIME);

export const SET_TIMEOUT_ACTIVE = "SET_TIMEOUT_ACTIVE";
export const setTimeoutActive = createAction(SET_TIMEOUT_ACTIVE);

export const SET_TOAST_MESSAGE = "SET_TOAST_MESSAGE";
export const setToastMessage = createAction(SET_TOAST_MESSAGE);

export const SHOW_DIALOG = "SHOW_DIALOG";
export const showDialog = createAction(SHOW_DIALOG);

export const HIDE_DIALOG = "HIDE_DIALOG";
export const hideDialog = createAction(HIDE_DIALOG);

export const ADD_USER_NOTIFICATION = "ADD_USER_NOTIFICATION";
export const addUserNotification = createAction(ADD_USER_NOTIFICATION);

export const ADD_ERROR_NOTIFICATION = "ADD_ERROR_NOTIFICATION";
export const addErrorNotification = createAction(ADD_ERROR_NOTIFICATION);

export const ADD_SUCCESS_NOTIFICATION = "ADD_SUCCESS_NOTIFICATION";
export const addSuccessNotification = createAction(ADD_SUCCESS_NOTIFICATION);

export const REMOVE_USER_NOTIFICATION = "REMOVE_USER_NOTIFICATION";
export const removeUserNotification = createAction(REMOVE_USER_NOTIFICATION);
