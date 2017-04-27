import configureTestStore from 'redux-asserts';
import sinon from 'sinon';

import {
  setSelectedKlassIndex,
  setPaymentAmount,
} from '../actions';
import rootReducer from '../reducers';
import { createAssertReducerResultState } from '../util/test_utils';


describe('reducers', () => {
  let sandbox, store, assertReducerResultState;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    store = configureTestStore(rootReducer);
    assertReducerResultState = createAssertReducerResultState(store, state => state.ui);
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe('ui', () => {
    it('should set the payment amount', () => {
      assertReducerResultState(setPaymentAmount, ui => ui.paymentAmount, '');
    });

    it('should set the selected klass index', () => {
      assertReducerResultState(setSelectedKlassIndex, ui => ui.selectedKlassIndex, undefined);
    });
  });

});
