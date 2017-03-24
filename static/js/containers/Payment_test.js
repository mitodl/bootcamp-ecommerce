import React from 'react';
import configureTestStore from 'redux-asserts';
import { mount } from 'enzyme';
import { Provider } from 'react-redux';
import { assert } from 'chai';
import sinon from 'sinon';

import * as api from '../lib/api';
import { setTotal } from '../actions';
import rootReducer from '../reducers';
import Payment from '../containers/Payment';
import * as util from '../util/util';
import { makeRequestActionType, makeReceiveSuccessActionType } from '../rest';

const REQUEST_PAYMENT = makeRequestActionType('payment');
const RECEIVE_PAYMENT_SUCCESS = makeReceiveSuccessActionType('payment');

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
    payment.find('input[id="total"]').props().onChange({
      target: {
        value: "123"
      }
    });
    assert.equal(store.getState().ui.total, "123");
  });

  it('sends a payment when API is contacted', () => {
    store.dispatch(setTotal("123"));
    sandbox.stub(api, 'fetchJSONWithCSRF').withArgs('/api/v0/payment/').returns(Promise.resolve());
    let payment = renderPayment();

    return listenForActions([REQUEST_PAYMENT, RECEIVE_PAYMENT_SUCCESS], () => {
      payment.find('.payment-button').simulate('click');
    });
  });

  it('constructs a form to be sent to Cybersource and submits it', () => {
    let url = '/x/y/z';
    let payload = {
      'pay': 'load'
    };
    sandbox.stub(api, 'fetchJSONWithCSRF').withArgs('/api/v0/payment/').returns(Promise.resolve({
      'url': url,
      'payload': payload
    }));

    let submitStub = sandbox.stub();
    let fakeForm = document.createElement("form");
    fakeForm.setAttribute("class", "fake-form");
    fakeForm.submit = submitStub;
    let createFormStub = sandbox.stub(util, 'createForm').returns(fakeForm);

    let wrapper = renderPayment();
    return listenForActions([REQUEST_PAYMENT, RECEIVE_PAYMENT_SUCCESS], () => {
      wrapper.find('.payment-button').simulate('click');
    }).then(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          assert.equal(createFormStub.callCount, 1);
          assert.deepEqual(createFormStub.args[0], [url, payload]);

          assert(document.body.querySelector(".fake-form"), 'fake form not found in body');
          assert.equal(submitStub.callCount, 1);
          assert.deepEqual(submitStub.args[0], []);

          resolve();
        }, 50);
      });
    });
  });
});
