// @flow
import { createAction } from 'redux-actions';

export const CLEAR_UI = 'CLEAR_UI';
export const clearUI = createAction(CLEAR_UI);

export const SET_PAYMENT_AMOUNT = 'SET_PAYMENT_AMOUNT';
export const setPaymentAmount = createAction(SET_PAYMENT_AMOUNT);

export const SET_SELECTED_KLASS_KEY = 'SET_SELECTED_KLASS_KEY';
export const setSelectedKlassKey = createAction(SET_SELECTED_KLASS_KEY);

export const FETCH_PROCESSING = 'FETCH_PROCESSING';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_FAILURE = 'FETCH_FAILURE';
