// @flow
import { createAction } from 'redux-actions';

import { fetchJSONWithCSRF } from './lib/api';
import {
  FETCH_PROCESSING,
  FETCH_SUCCESS,
  FETCH_FAILURE,
} from './actions';

const endpoints = [
  {
    name: 'payment',
    prefix: '',
    url: '/api/v0/payment/',
    makeOptions: total => ({
      method: 'POST',
      body: JSON.stringify({
        total: total,
      })
    }),
  },
];

export const makeRequestActionType = reducerName => `REQUEST_${reducerName.toUpperCase()}`;
export const makeReceiveSuccessActionType = reducerName => `RECEIVE_${reducerName.toUpperCase()}_SUCCESS`;
export const makeReceiveFailureActionType = reducerName => `RECEIVE_${reducerName.toUpperCase()}_FAILURE`;
export const makeClearType = reducerName => `CLEAR_${reducerName.toUpperCase()}`;

const makeReducer = (reducerName, initialState = {}) => {
  const requestType = makeRequestActionType(reducerName);
  const receiveSuccessType = makeReceiveSuccessActionType(reducerName);
  const receiveFailureType = makeReceiveFailureActionType(reducerName);
  const clearType = makeClearType(reducerName);

  return (state = initialState, action) => {
    switch (action.type) {
      case [requestType]:
        return {
          ...state,
          fetchStatus: FETCH_PROCESSING,
        };
      case [receiveSuccessType]:
        return {
          ...state,
          fetchStatus: FETCH_SUCCESS,
          data: action.payload,
        };
      case [receiveFailureType]:
        return {
          ...state,
          fetchStatus: FETCH_FAILURE,
          error: action.payload,
        };
      case [clearType]:
        return initialState;
      default:
        return state;
    }
  }
};

const _reducers = {};
const _actions = {};
for (const endpoint of endpoints) {
  _reducers[endpoint.name] = makeReducer(endpoint.name);

  let fetchFunc = (...args) => {
    let options = endpoint.makeOptions(...args);
    return fetchJSONWithCSRF(endpoint.url, options);
  };

  const requestAction = createAction(makeRequestActionType(endpoint.name));
  const receiveSuccessAction = createAction(makeReceiveSuccessActionType(endpoint.name));
  const receiveFailureAction = createAction(makeReceiveFailureActionType(endpoint.name));

  _actions[endpoint.name] = (...params) => {
    return dispatch => {
      dispatch(requestAction());
      fetchFunc(...params).then(data => {
        dispatch(receiveSuccessAction(data));
        return Promise.resolve();
      }).catch(error => {
        dispatch(receiveFailureAction(error));
        return Promise.reject();
      });
    };
  }
}
export const reducers = _reducers;
export const actions = _actions;
