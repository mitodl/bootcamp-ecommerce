import { combineReducers } from 'redux';
import {
    UPDATE_CHECKBOX
} from '../actions';

const INITIAL_CHECKBOX_STATE = {
  checked: false
};

export const checkbox = (state = INITIAL_CHECKBOX_STATE, action) => {
  switch (action.type) {
  case UPDATE_CHECKBOX:
    return Object.assign({}, state, {
      checked: action.payload.checked
    });
  default:
    return state;
  }
};

export default combineReducers({
  checkbox
});

