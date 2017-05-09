import configureTestStore from 'redux-asserts';
import sinon from 'sinon';
import moment from 'moment';
import { assert } from 'chai';

import {
  setSelectedKlassKey,
  setPaymentAmount,
  setInitialTime,
  setTimeoutActive,
  setToastMessage,
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
      assertReducerResultState(setSelectedKlassKey, ui => ui.selectedKlassKey, undefined);
    });

    it('should let you set the initial time, and the default is a valid time', () => {
      let initialTime = store.getState().ui.initialTime;
      assert.isTrue(moment(initialTime).isValid());

      assertReducerResultState(setInitialTime, ui => ui.initialTime, initialTime);
    });

    it('should set timeoutActive', () => {
      assertReducerResultState(setTimeoutActive, ui => ui.timeoutActive, false);
    });

    it('should set the toast message', () => {
      assertReducerResultState(setToastMessage, ui => ui.toastMessage, null);
    });
  });
});
