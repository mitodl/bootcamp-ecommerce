// @flow
import { createAction } from 'redux-actions';

import { fetchJSONWithCSRF } from './lib/api';
import {
  FETCH_PROCESSING,
  FETCH_SUCCESS,
  FETCH_FAILURE,
} from './actions';

export const makeRequestActionType = reducerName => `REQUEST_${reducerName.toUpperCase()}`;
export const makeReceiveSuccessActionType = reducerName => `RECEIVE_${reducerName.toUpperCase()}_SUCCESS`;
export const makeReceiveFailureActionType = reducerName => `RECEIVE_${reducerName.toUpperCase()}_FAILURE`;
export const makeClearType = reducerName => `CLEAR_${reducerName.toUpperCase()}`;

const INITIAL_STATE = {
  loaded: false,
  processing: false,
};
export const makeReducer = (endpoint, initialState = INITIAL_STATE) => {
  const reducerName = endpoint.name;
  const requestType = makeRequestActionType(reducerName);
  const receiveSuccessType = makeReceiveSuccessActionType(reducerName);
  const receiveFailureType = makeReceiveFailureActionType(reducerName);
  const clearType = makeClearType(reducerName);

  return (state = initialState, action) => {
    switch (action.type) {
    case requestType:
      return {
        ...state,
        fetchStatus: FETCH_PROCESSING,
        loaded: false,
        processing: true,
      };
    case receiveSuccessType:
      return {
        ...state,
        fetchStatus: FETCH_SUCCESS,
        data: action.payload,
        loaded: true,
        processing: false,
      };
    case receiveFailureType:
      return {
        ...state,
        fetchStatus: FETCH_FAILURE,
        error: action.payload,
        loaded: true,
        processing: false,
      };
    case clearType:
      return initialState;
    default:
      return state;
    }
  };
};

export const makeFetchFunc = endpoint => (
  (...args) => fetchJSONWithCSRF(endpoint.url, endpoint.makeOptions(...args))
);

export const makeAction = (endpoint) => {
  const requestAction = createAction(makeRequestActionType(endpoint.name));
  const receiveSuccessAction = createAction(makeReceiveSuccessActionType(endpoint.name));
  const receiveFailureAction = createAction(makeReceiveFailureActionType(endpoint.name));

  const fetchFunc = makeFetchFunc(endpoint);

  return (...params) => {
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
  };
};

export const endpoints = [
  {
    name: 'payment',
    url: '/api/v0/payment/',
    makeOptions: total => ({
      method: 'POST',
      body: JSON.stringify({
        total: total,
      })
    }),
  },
];

const reducers = {};
const actions = {};
for (const endpoint of endpoints) {
  reducers[endpoint.name] = makeReducer(endpoint);
  actions[endpoint.name] = makeAction(endpoint);
}
export { reducers, actions };
