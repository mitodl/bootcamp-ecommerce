// @flow
import { combineReducers } from 'redux';

import { SET_TOTAL } from '../actions';
import type { Action } from '../flow/reduxTypes';
import { reducers as restReducers } from '../rest';

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
  ui,
  ...restReducers,
});
