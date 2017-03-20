// @flow
import { createAction } from 'redux-actions';
import type { Dispatch } from 'redux';

import type { Dispatcher } from '../flow/reduxTypes';

export const SET_TOTAL = 'SET_TOTAL';
export const setTotal = createAction(SET_TOTAL);

export const FETCH_PROCESSING = 'FETCH_PROCESSING';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_FAILURE = 'FETCH_FAILURE';
