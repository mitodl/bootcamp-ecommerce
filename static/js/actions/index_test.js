import { assertCreatedActionHelper } from './test_util';

import {
  requestPayment,
  receivePaymentSuccess,
  receivePaymentFailure,
  setTotal,

  REQUEST_PAYMENT,
  RECEIVE_PAYMENT_SUCCESS,
  RECEIVE_PAYMENT_FAILURE,
  SET_TOTAL,
} from './index';

describe('actions', () => {
  it('should create all action creators', () => {
    [
      [requestPayment, REQUEST_PAYMENT],
      [receivePaymentSuccess, RECEIVE_PAYMENT_SUCCESS],
      [receivePaymentFailure, RECEIVE_PAYMENT_FAILURE],
      [setTotal, SET_TOTAL],
    ].forEach(assertCreatedActionHelper);
  });
});
