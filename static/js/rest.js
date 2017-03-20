// @flow
import { createAction } from 'redux-actions';

import { fetchJSONWithCSRF } from './lib/api_util';

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

const makeReducer = (reducerName, initialState = {}) => (
  (state = initialState, action) => {
    switch (action.type) {
    case [makeRequestActionType(reducerName)]:
      return {
        ...state,
        fetchStatus: FETCH_PROCESSING,
      };
    case [makeReceiveSuccessActionType(reducerName)]:
      return {
        ...state,
        fetchStatus: FETCH_SUCCESS,
        data: action.payload,
      };
    case [makeReceiveFailureActionType(reducerName)]:
      return {
        ...state,
        fetchStatus: FETCH_FAILURE,
        error: action.payload,
      };
    case [makeClearType(reducerName)]:
      return initialState;
    default:
      return state;
    }
  }
);

const _reducers = {};
const _actions = {};
for (const endpoint of endpoints) {
  _reducers[endpoint.name] = makeReducer(endpoint.name);

  let fetchFunc = (...args) => {
    let options = endpoint.makeOptions(...args);
    return fetchJSONWithCSRF(endpoint.url, options);
  };

  _actions[endpoint.name] = (...params) => {
    return dispatch => {
      dispatch(createAction(makeRequestActionType(endpoint.name))());
      fetchFunc(...params).then(data => {
        dispatch(createAction(makeReceiveSuccessActionType(endpoint.name))(data));
        return Promise.resolve();
      }).catch(error => {
        dispatch(createAction(makeReceiveFailureActionType(endpoint.name))(error));
        return Promise.reject();
      });
    };
  }
}
export const reducers = _reducers;
export const actions = _actions;
