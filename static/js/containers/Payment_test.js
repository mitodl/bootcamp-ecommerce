/* global SETTINGS: false */
import React from 'react';
import configureTestStore from 'redux-asserts';
import { mount } from 'enzyme';
import { Provider } from 'react-redux';
import { assert } from 'chai';
import sinon from 'sinon';
import _ from 'lodash';
import moment from 'moment';

import * as api from '../lib/api';
import {
  setPaymentAmount,
  setSelectedKlassIndex
} from '../actions';
import rootReducer from '../reducers';
import Payment from '../containers/Payment';
import * as util from '../util/util';
import {
  makeRequestActionType,
  makeReceiveSuccessActionType
} from '../rest';

const REQUEST_PAYMENT = makeRequestActionType('payment');
const RECEIVE_PAYMENT_SUCCESS = makeReceiveSuccessActionType('payment');
const REQUEST_KLASSES = makeRequestActionType('klasses');
const RECEIVE_KLASSES_SUCCESS = makeReceiveSuccessActionType('klasses');

const generateFakeKlasses = (numKlasses = 1) => {
  return _.times(numKlasses, (i) => ({
    klass_name: `Bootcamp 1 Klass ${i}`,
    klass_key: i + 1,
    payment_deadline: moment()
  }));
};

describe('Payment container', () => {
  const klassTitleSelector = '.klass-display-section',
    klassDropdownSelector = 'select.klass-select',
    welcomeMsgSelector = 'h1.greeting',
    paymentInputSelector = 'input[id="payment-amount"]',
    paymentBtnSelector = 'button.large-cta',
    deadlineMsgSelector = '.deadline-date';

  let store, listenForActions, sandbox, fetchStub,
    klassesUrl, klassesStub; // eslint-disable-line no-unused-vars

  beforeEach(() => {
    SETTINGS.user = {
      full_name: "john doe",
      username: "johndoe"
    };

    store = configureTestStore(rootReducer);
    listenForActions = store.createListenForActions();
    sandbox = sinon.sandbox.create();
    fetchStub = sandbox.stub(api, 'fetchJSONWithCSRF');
    klassesUrl = `/api/v0/klasses/${SETTINGS.user.username}/`;
  });

  afterEach(() => {
    sandbox.restore();
  });

  let renderPaymentComponent = (props = {}) => (
    mount(
      <Provider store={store}>
        <Payment {...props} />
      </Provider>
    )
  );

  let renderFullPaymentPage = (props = {}) => {
    let wrapper;
    return listenForActions([REQUEST_KLASSES, RECEIVE_KLASSES_SUCCESS], () => {
      wrapper = renderPaymentComponent(props);
    }).then(() => {
      return Promise.resolve(wrapper);
    });
  };

  it('does not have a selected klass by default', () => {
    let fakeKlasses = generateFakeKlasses(3);
    klassesStub = fetchStub.withArgs(klassesUrl)
      .returns(Promise.resolve(fakeKlasses));

    return renderFullPaymentPage().then((wrapper) => {
      assert.isUndefined(wrapper.find('Payment').prop('selectedKlass'));
    });
  });

  it('sets a selected klass', () => {
    let fakeKlasses = generateFakeKlasses(3);
    klassesStub = fetchStub.withArgs(klassesUrl)
      .returns(Promise.resolve(fakeKlasses));
    store.dispatch(setSelectedKlassIndex(2));

    return renderFullPaymentPage().then((wrapper) => {
      assert.deepEqual(wrapper.find('Payment').prop('selectedKlass'), fakeKlasses[2]);
    });
  });

  describe('UI', () => {
    it('shows the name of the user in a welcome message', () => {
      let fakeKlasses = generateFakeKlasses();
      klassesStub = fetchStub.withArgs(klassesUrl)
        .returns(Promise.resolve(fakeKlasses));

      return renderFullPaymentPage().then((wrapper) => {
        let welcomeMsg = wrapper.find(welcomeMsgSelector);
        assert.include(welcomeMsg.text(), SETTINGS.user.full_name);
      });
    });

    it('shows the selected klass', () => {
      let fakeKlasses = generateFakeKlasses(3);
      klassesStub = fetchStub.withArgs(klassesUrl)
        .returns(Promise.resolve(fakeKlasses));
      store.dispatch(setSelectedKlassIndex(0));

      return renderFullPaymentPage().then((wrapper) => {
        let title = wrapper.find(klassTitleSelector);
        assert.include(title.text(), fakeKlasses[0].klass_name);
      });
    });

    it('does not show the welcome message if the name of the user is blank', () => {
      SETTINGS.user.full_name = '';
      klassesStub = fetchStub
        .withArgs(klassesUrl)
        .returns(Promise.resolve(generateFakeKlasses(1)));
      return renderFullPaymentPage().then((wrapper) => {
        assert.isFalse(wrapper.find(welcomeMsgSelector).exists());
      });
    });

    [
      [1, false],
      [2, true]
    ].forEach(([numKlasses, shouldShowDropdown]) => {
      it(`dropdown is ${shouldShowDropdown ? '' : 'not'} visible when ${numKlasses} klasses available`, () => {
        let fakeKlasses = generateFakeKlasses(numKlasses);
        klassesStub = fetchStub.withArgs(klassesUrl)
          .returns(Promise.resolve(fakeKlasses));

        return renderFullPaymentPage().then((wrapper) => {
          assert.equal(wrapper.find(klassDropdownSelector).exists(), shouldShowDropdown);
        });
      });
    });

    [
      [moment().format(), 'non-null date message'],
      [null, 'null date message']
    ].forEach(([deadlineDateISO, deadlineDateDesc]) => {
      it(`shows payment due date message with ${deadlineDateDesc}`, () => {
        let fakeKlasses = generateFakeKlasses(1);
        fakeKlasses[0].payment_deadline = deadlineDateISO;
        klassesStub = fetchStub.withArgs(klassesUrl)
          .returns(Promise.resolve(fakeKlasses));
        store.dispatch(setSelectedKlassIndex(0));

        return renderFullPaymentPage().then((wrapper) => {
          let deadlineText = wrapper.find(deadlineMsgSelector).text();
          assert.include(deadlineText, 'You can pay any amount');
          if (!_.isEmpty(deadlineDateISO)) {
            assert.include(deadlineText, moment(deadlineDateISO).format("MMM D, YYYY"));
          }
        });
      });
    });
  });

  describe('payment functionality', () => {
    beforeEach(() => {
      klassesStub = fetchStub
        .withArgs(klassesUrl)
        .returns(Promise.resolve(generateFakeKlasses(1)));
      store.dispatch(setSelectedKlassIndex(0));
    });

    it('sets a price', () => {
      return renderFullPaymentPage().then((wrapper) => {
        wrapper.find(paymentInputSelector).props().onChange({
          target: {
            value: "123"
          }
        });
        assert.equal(store.getState().ui.paymentAmount, "123");
      });
    });

    it('sends a payment when API is contacted', () => {
      store.dispatch(setPaymentAmount("123"));
      fetchStub.withArgs('/api/v0/payment/').returns(Promise.resolve());
      return renderFullPaymentPage().then((wrapper) => {
        return listenForActions([REQUEST_PAYMENT, RECEIVE_PAYMENT_SUCCESS], () => {
          wrapper.find(paymentBtnSelector).simulate('click');
        });
      });
    });

    it('constructs a form to be sent to Cybersource and submits it', () => {
      let url = '/x/y/z';
      let payload = {
        'pay': 'load'
      };
      fetchStub.withArgs('/api/v0/payment/').returns(Promise.resolve({
        'url': url,
        'payload': payload
      }));

      let submitStub = sandbox.stub();
      let fakeForm = document.createElement("form");
      fakeForm.setAttribute("class", "fake-form");
      fakeForm.submit = submitStub;
      let createFormStub = sandbox.stub(util, 'createForm').returns(fakeForm);

      return renderFullPaymentPage().then((wrapper) => {
        return listenForActions([REQUEST_PAYMENT, RECEIVE_PAYMENT_SUCCESS], () => {
          wrapper.find(paymentBtnSelector).simulate('click');
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
  });
});
