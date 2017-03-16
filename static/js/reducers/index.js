// @flow
import { combineReducers } from 'redux';
import {
  FETCH_PROCESSING,
  FETCH_SUCCESS,
  FETCH_FAILURE,

  REQUEST_PAYMENT,
  RECEIVE_PAYMENT_SUCCESS,
  RECEIVE_PAYMENT_FAILURE,
  SET_TOTAL,
} from '../actions';
import type { Action } from '../flow/reduxTypes';

export type PaymentState = {
  fetchStatus?: string,
};
const INITIAL_PAYMENT_STATE: PaymentState = {};

export const payment = (state: PaymentState = INITIAL_PAYMENT_STATE, action: Action) => {
  switch (action.type) {
  case REQUEST_PAYMENT:
    return { ...state, fetchStatus: FETCH_PROCESSING };
  case RECEIVE_PAYMENT_SUCCESS:
    return { ...state, fetchStatus: FETCH_SUCCESS };
  case RECEIVE_PAYMENT_FAILURE:
    return { ...state, fetchStatus: FETCH_FAILURE };
  default:
    return state;
  }
};

export type UIState = {
  total: string,
};
const INITIAL_UI_STATE = {
  total: ''
};

export const ui = (state: UIState = INITIAL_UI_STATE, action: Action) => {
  switch (action.type) {
  case SET_TOTAL:
    return { ...state, total: action.payload };
  default:
    return state;
  }
};

export default combineReducers({
  payment,
  ui,
});
