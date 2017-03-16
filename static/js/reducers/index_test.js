import { assert } from 'chai';
import configureTestStore from 'redux-asserts';
import sinon from 'sinon';

import {
  sendPayment,
  setTotal,

  REQUEST_PAYMENT,
  RECEIVE_PAYMENT_SUCCESS,
  RECEIVE_PAYMENT_FAILURE,

  FETCH_PROCESSING,
  FETCH_SUCCESS,
  FETCH_FAILURE,
} from '../actions';
import * as api from '../lib/api';
import rootReducer from '../reducers';

describe('reducers', () => {
  let sandbox, store;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    store = configureTestStore(rootReducer);
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe('payment', () => {
    let dispatchThen, sendPaymentStub;
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.payment);
      sendPaymentStub = sandbox.stub(api, 'sendPayment');
    });

    it('should send a payment', () => {
      sendPaymentStub.returns(Promise.resolve());

      let total = 'total';
      return dispatchThen(sendPayment(total), [REQUEST_PAYMENT, RECEIVE_PAYMENT_SUCCESS]).then(state => {
        assert.deepEqual(state, {
          fetchStatus: FETCH_SUCCESS,
        });
        assert.isTrue(sendPaymentStub.calledWith(total));
      });
    });

    it('should fail to send a payment', () => {
      sendPaymentStub.returns(Promise.reject());

      let total = 'total';
      return dispatchThen(sendPayment(total), [REQUEST_PAYMENT, RECEIVE_PAYMENT_FAILURE]).then(state => {
        assert.deepEqual(state, {
          fetchStatus: FETCH_FAILURE,
        });
        assert.isTrue(sendPaymentStub.calledWith(total));
      });
    });

    it('should be processing right after starting the API call', () => {
      sendPaymentStub.returns(new Promise(() => {}));

      let total = 'total';
      return dispatchThen(sendPayment(total), [REQUEST_PAYMENT]).then(state => {
        assert.deepEqual(state, {
          fetchStatus: FETCH_PROCESSING
        });
        assert.isTrue(sendPaymentStub.calledWith(total));
      });
    });
  });

  describe('ui', () => {
    it('should set the total price', () => {
      assert.equal(store.getState().ui.total, '');
      store.dispatch(setTotal("price"));
      assert.equal(store.getState().ui.total, "price");
    });
  });

});
