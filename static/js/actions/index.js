// @flow
import { createAction } from 'redux-actions';
import type { Dispatch } from 'redux';

import * as api from '../lib/api';
import type { PaymentResponse } from '../lib/api';
import type { Dispatcher } from '../flow/reduxTypes';

export const REQUEST_PAYMENT = 'REQUEST_PAYMENT';
export const RECEIVE_PAYMENT_SUCCESS = 'RECEIVE_PAYMENT_SUCCESS';
export const RECEIVE_PAYMENT_FAILURE = 'RECEIVE_PAYMENT_FAILURE';

export const SET_TOTAL = 'SET_TOTAL';


export const requestPayment = createAction(REQUEST_PAYMENT);
export const receivePaymentSuccess = createAction(RECEIVE_PAYMENT_SUCCESS);
export const receivePaymentFailure = createAction(RECEIVE_PAYMENT_FAILURE);

export const sendPayment = (total: string): Dispatcher<PaymentResponse> => {
  return (dispatch: Dispatch) => {
    dispatch(requestPayment(total));
    return api.sendPayment(total).then(response => {
      dispatch(receivePaymentSuccess(response));
    }).catch(error => {
      dispatch(receivePaymentFailure(error));
    });
  };
};

export const setTotal = createAction(SET_TOTAL);

export const FETCH_PROCESSING = 'FETCH_PROCESSING';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_FAILURE = 'FETCH_FAILURE';
