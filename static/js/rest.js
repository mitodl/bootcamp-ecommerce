// @flow
import { createAction } from 'redux-actions';
import type { Dispatch } from 'redux';

import type { Action, Dispatcher } from './flow/reduxTypes';
import { fetchJSONWithCSRF } from './lib/api';
import {
  FETCH_PROCESSING,
  FETCH_SUCCESS,
  FETCH_FAILURE,
} from './actions';

export type Endpoint = {
  name: string,
  url: string,
  makeOptions: (...args: any) => Object
};

export const makeRequestActionType = (reducerName: string) => `REQUEST_${reducerName.toUpperCase()}`;
export const makeReceiveSuccessActionType = (reducerName: string) => `RECEIVE_${reducerName.toUpperCase()}_SUCCESS`;
export const makeReceiveFailureActionType = (reducerName: string) => `RECEIVE_${reducerName.toUpperCase()}_FAILURE`;
export const makeClearType = (reducerName: string) => `CLEAR_${reducerName.toUpperCase()}`;

export type RestState = {
  data?: any,
  error?: any,
  processing: boolean,
  loaded: boolean,
  fetchStatus?: string,
};

const INITIAL_STATE: RestState = {
  loaded: false,
  processing: false,
};
export const makeReducer = (endpoint: Endpoint, initialState: RestState = INITIAL_STATE) => {
  const reducerName = endpoint.name;
  const requestType = makeRequestActionType(reducerName);
  const receiveSuccessType = makeReceiveSuccessActionType(reducerName);
  const receiveFailureType = makeReceiveFailureActionType(reducerName);
  const clearType = makeClearType(reducerName);

  return (state: Object = initialState, action: Action) => {
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

export function makeFetchFunc(endpoint: Endpoint): (...args: any) => Promise<*> {
  return (...args) => fetchJSONWithCSRF(endpoint.url, endpoint.makeOptions(...args));
}

export const makeAction = (endpoint: Endpoint): ((...params: any) => Dispatcher<*>) => {
  const requestAction = createAction(makeRequestActionType(endpoint.name));
  const receiveSuccessAction = createAction(makeReceiveSuccessActionType(endpoint.name));
  const receiveFailureAction = createAction(makeReceiveFailureActionType(endpoint.name));

  const fetchFunc = makeFetchFunc(endpoint);

  return (...params) => {
    return (dispatch: Dispatch): Promise<*> => {
      dispatch(requestAction());
      return fetchFunc(...params).then(data => {
        dispatch(receiveSuccessAction(data));
        return Promise.resolve(data);
      }).catch(error => {
        dispatch(receiveFailureAction(error));
        return Promise.reject(error);
      });
    };
  };
};

export const endpoints: Array<Endpoint> = [
  {
    name: 'payment',
    url: '/api/v0/payment/',
    makeOptions: (total, klassId) => ({
      method: 'POST',
      body: JSON.stringify({
        total: total,
        klass_id: klassId,
      })
    }),
  },
];

const reducers: Object = {};
const actions: Object = {};
for (const endpoint of endpoints) {
  reducers[endpoint.name] = makeReducer(endpoint);
  actions[endpoint.name] = makeAction(endpoint);
}
export { reducers, actions };
