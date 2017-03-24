// @flow
import { createAction } from 'redux-actions';

export const SET_TOTAL = 'SET_TOTAL';
export const setTotal = createAction(SET_TOTAL);

export const SET_KLASS_ID = 'SET_KLASS_ID';
export const setKlassId = createAction(SET_KLASS_ID);

export const FETCH_PROCESSING = 'FETCH_PROCESSING';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_FAILURE = 'FETCH_FAILURE';
