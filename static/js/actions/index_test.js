import { assertCreatedActionHelper } from './test_util';

import {
  setSelectedKlassKey,
  setPaymentAmount,
  SET_SELECTED_KLASS_KEY,
  SET_PAYMENT_AMOUNT,
} from './index';

describe('actions', () => {
  it('should create all action creators', () => {
    [
      [setPaymentAmount, SET_PAYMENT_AMOUNT],
      [setSelectedKlassKey, SET_SELECTED_KLASS_KEY],
    ].forEach(assertCreatedActionHelper);
  });
});
