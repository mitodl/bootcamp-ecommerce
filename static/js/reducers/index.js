// @flow
import { combineReducers } from 'redux';

import {
  CLEAR_UI,
  SET_SELECTED_KLASS_INDEX,
  SET_PAYMENT_AMOUNT
} from '../actions';
import type { Action } from '../flow/reduxTypes';
import { reducers as restReducers } from '../rest';

export type UIState = {
  paymentAmount: string,
  selectedKlassIndex?: number
};
const INITIAL_UI_STATE = {
  paymentAmount: ''
};

export const ui = (state: UIState = INITIAL_UI_STATE, action: Action) => {
  switch (action.type) {
  case CLEAR_UI:
    return INITIAL_UI_STATE;
  case SET_PAYMENT_AMOUNT:
    return { ...state, paymentAmount: action.payload };
  case SET_SELECTED_KLASS_INDEX:
    return { ...state, selectedKlassIndex: action.payload };
  default:
    return state;
  }
};

export default combineReducers({
  ui,
  ...restReducers,
});
