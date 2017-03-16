// @flow
import React from 'react';
import configureTestStore from 'redux-asserts';
import { mount } from 'enzyme';
import { Provider } from 'react-redux';
import { assert } from 'chai';
import sinon from 'sinon';

import * as api from '../lib/api';
import {
  REQUEST_PAYMENT,
  RECEIVE_PAYMENT_SUCCESS,
  setTotal,
} from '../actions';
import rootReducer from '../reducers';
import Payment from '../containers/Payment';

describe('Payment', () => {
  let store, listenForActions, sandbox;
  beforeEach(() => {
    store = configureTestStore(rootReducer);
    sandbox = sinon.sandbox.create();
    listenForActions = store.createListenForActions();
  });
  afterEach(() => {
    sandbox.restore();
  });

  let renderPayment = () => {
    return mount(
      <Provider store={store}>
        <Payment />
      </Provider>
    );
  };

  it('sets a price', () => {
    let payment = renderPayment();
    payment.find('input[type="number"]').props().onChange({
      target: {
        value: "123"
      }
    });
    assert.equal(store.getState().ui.total, "123");
  });

  it('sends a payment when API is contacted', () => {
    store.dispatch(setTotal("123"));
    sandbox.stub(api, 'sendPayment').returns(Promise.resolve());
    let payment = renderPayment();

    return listenForActions([REQUEST_PAYMENT, RECEIVE_PAYMENT_SUCCESS], () => {
      payment.find('.payment-button').simulate('click');
    });
  });
});
