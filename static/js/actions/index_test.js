import { assertCreatedActionHelper } from './test_util';

import {
  setSelectedKlassIndex,
  setPaymentAmount,
  SET_SELECTED_KLASS_INDEX,
  SET_PAYMENT_AMOUNT,
} from './index';

describe('actions', () => {
  it('should create all action creators', () => {
    [
      [setPaymentAmount, SET_PAYMENT_AMOUNT],
      [setSelectedKlassIndex, SET_SELECTED_KLASS_INDEX],
    ].forEach(assertCreatedActionHelper);
  });
});
