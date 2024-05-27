// @flow
import moment from "moment";
import { mergeRight, omit } from "ramda";

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
  REMOVE_USER_NOTIFICATION,
  ADD_ERROR_NOTIFICATION,
  ADD_SUCCESS_NOTIFICATION,
} from "../actions";
import {
  ALERT_TYPE_ERROR,
  ALERT_TYPE_SUCCESS,
  APP_NOTIFICATION,
} from "../constants";

import type { Action } from "../flow/reduxTypes";
import type { UserNotificationMapping } from "../flow/uiTypes";

export type ToastMessage = {
  message: string,
  title?: string,
  icon?: string,
};

export type UIState = {
  paymentAmount: string,
  selectedBootcampRunKey?: number,
  initialTime: string,
  timeoutActive: boolean,
  toastMessage: ?ToastMessage,
  dialogVisibility: Object,
  userNotifications: UserNotificationMapping,
};

const INITIAL_UI_STATE: UIState = {
  paymentAmount: "",
  initialTime: moment().toISOString(),
  timeoutActive: false,
  toastMessage: null,
  dialogVisibility: {},
  userNotifications: {},
};

const ui = (state: UIState = INITIAL_UI_STATE, action: Action) => {
  switch (action.type) {
    case CLEAR_UI:
      return INITIAL_UI_STATE;
    case SET_PAYMENT_AMOUNT:
      return { ...state, paymentAmount: action.payload };
    case SET_SELECTED_BOOTCAMP_RUN_KEY:
      return { ...state, selectedBootcampRunKey: action.payload };
    case SET_INITIAL_TIME:
      return { ...state, initialTime: action.payload };
    case SET_TIMEOUT_ACTIVE:
      return { ...state, timeoutActive: action.payload };
    case SET_TOAST_MESSAGE:
      return { ...state, toastMessage: action.payload };
    case SHOW_DIALOG:
      return {
        ...state,
        dialogVisibility: {
          ...state.dialogVisibility,
          [action.payload]: true,
        },
      };
    case HIDE_DIALOG:
      return {
        ...state,
        dialogVisibility: {
          ...state.dialogVisibility,
          [action.payload]: false,
        },
      };
    case ADD_USER_NOTIFICATION:
      return {
        ...state,
        userNotifications: mergeRight(state.userNotifications, action.payload),
      };
    case ADD_ERROR_NOTIFICATION:
      return {
        ...state,
        userNotifications: mergeRight(state.userNotifications, {
          [APP_NOTIFICATION]: {
            type: ALERT_TYPE_ERROR,
            ...action.payload,
          },
        }),
      };
    case ADD_SUCCESS_NOTIFICATION:
      return {
        ...state,
        userNotifications: mergeRight(state.userNotifications, {
          [APP_NOTIFICATION]: {
            type: ALERT_TYPE_SUCCESS,
            ...action.payload,
          },
        }),
      };
    case REMOVE_USER_NOTIFICATION:
      return {
        ...state,
        userNotifications: omit([action.payload], state.userNotifications),
      };
    default:
      return state;
  }
};

export default ui;
