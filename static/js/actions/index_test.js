import { assertCreatedActionHelper } from './test_util';

import {
  setSelectedKlassKey,
  setPaymentAmount,
  setInitialTime,
  setTimeoutActive,
  setToastMessage,
  SET_SELECTED_KLASS_KEY,
  SET_PAYMENT_AMOUNT,
  SET_INITIAL_TIME,
  SET_TIMEOUT_ACTIVE,
  SET_TOAST_MESSAGE,
} from './index';

describe('actions', () => {
  it('should create all action creators', () => {
    [
      [setPaymentAmount, SET_PAYMENT_AMOUNT],
      [setSelectedKlassKey, SET_SELECTED_KLASS_KEY],
      [setInitialTime, SET_INITIAL_TIME],
      [setTimeoutActive, SET_TIMEOUT_ACTIVE],
      [setToastMessage, SET_TOAST_MESSAGE],
    ].forEach(assertCreatedActionHelper);
  });
});
