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
  setSelectedKlassKey,
  setInitialTime,
  setToastMessage,
  SET_TIMEOUT_ACTIVE,
  SET_TOAST_MESSAGE,
} from '../actions';
import {
  TOAST_SUCCESS,
  TOAST_FAILURE,
} from '../constants';
import rootReducer from '../reducers';
import PaymentPage from './PaymentPage';
import * as util from '../util/util';
import { generateFakeKlasses } from '../factories';
import {
  makeRequestActionType,
  makeReceiveSuccessActionType
} from '../rest';

const REQUEST_PAYMENT = makeRequestActionType('payment');
const RECEIVE_PAYMENT_SUCCESS = makeReceiveSuccessActionType('payment');
const REQUEST_KLASSES = makeRequestActionType('klasses');
const RECEIVE_KLASSES_SUCCESS = makeReceiveSuccessActionType('klasses');

describe('PaymentPage', () => {
  const klassTitleSelector = '.klass-display-section .desc',
    klassDropdownSelector = 'select.klass-select',
    welcomeMsgSelector = 'h1.greeting',
    paymentInputSelector = 'input[id="payment-amount"]',
    paymentBtnSelector = 'button.large-cta',
    deadlineMsgSelector = '.deadline-message';

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
        <PaymentPage {...props} />
      </Provider>
    )
  );

  let renderFullPaymentPage = (props = {}, extraActions = []) => {
    let wrapper;
    let actions = [REQUEST_KLASSES, RECEIVE_KLASSES_SUCCESS].concat(extraActions);
    return listenForActions(actions, () => {
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
      assert.isUndefined(wrapper.find('PaymentPage').prop('selectedKlass'));
    });
  });

  it('sets a selected klass', () => {
    let fakeKlasses = generateFakeKlasses(3);
    klassesStub = fetchStub.withArgs(klassesUrl)
      .returns(Promise.resolve(fakeKlasses));
    store.dispatch(setSelectedKlassKey(3));

    return renderFullPaymentPage().then((wrapper) => {
      assert.deepEqual(wrapper.find('PaymentPage').prop('selectedKlass'), fakeKlasses[2]);
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
      store.dispatch(setSelectedKlassKey(1));

      return renderFullPaymentPage().then((wrapper) => {
        let title = wrapper.find(klassTitleSelector);
        assert.include(title.text(), fakeKlasses[0].display_title);
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
      it(`should ${shouldShowDropdown ? '' : 'not'} show dropdown when ${numKlasses} klasses available`, () => {
        let fakeKlasses = generateFakeKlasses(numKlasses);
        klassesStub = fetchStub.withArgs(klassesUrl)
          .returns(Promise.resolve(fakeKlasses));

        return renderFullPaymentPage().then((wrapper) => {
          assert.equal(wrapper.find(klassDropdownSelector).exists(), shouldShowDropdown);
        });
      });
    });

    it('only shows payable klasses in the klass dropdown', () => {
      let fakeKlasses = generateFakeKlasses(3);
      fakeKlasses[1].is_user_eligible_to_pay = false;
      klassesStub = fetchStub.withArgs(klassesUrl)
        .returns(Promise.resolve(fakeKlasses));

      return renderFullPaymentPage().then((wrapper) => {
        assert.lengthOf(wrapper.find('Payment').prop('payableKlassesData'), 2);
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
        store.dispatch(setSelectedKlassKey(1));

        return renderFullPaymentPage().then((wrapper) => {
          let deadlineText = wrapper.find(deadlineMsgSelector).text();
          assert.include(deadlineText, 'You can pay any amount');
          if (!_.isEmpty(deadlineDateISO)) {
            assert.include(deadlineText, util.formatReadableDate(moment(deadlineDateISO)));
          }
        });
      });
    });

    [
      [100, true, "past payments should"],
      [0, false, "no past payments should not"]
    ].forEach(([totalPaid, shouldShowPayHistory, testDesciption]) => {
      it(`for user with ${testDesciption} include payment history component`, () => {
        let fakeKlasses = generateFakeKlasses(2);
        for (let klass of fakeKlasses) {
          klass.total_paid = totalPaid;
        }
        klassesStub = fetchStub.withArgs(klassesUrl)
          .returns(Promise.resolve(fakeKlasses));

        return renderFullPaymentPage().then((wrapper) => {
          assert.equal(wrapper.find('PaymentHistory').exists(), shouldShowPayHistory);
        });
      });
    });
  });

  describe('payment functionality', () => {
    beforeEach(() => {
      klassesStub = fetchStub
        .withArgs(klassesUrl)
        .returns(Promise.resolve(generateFakeKlasses(1)));
      store.dispatch(setSelectedKlassKey(1));
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
      store.dispatch(setPaymentAmount("123"));

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

  describe('order receipt and cancellation pages', () => {
    const TOAST_ACTIONS = [SET_TOAST_MESSAGE];
    const TIMEOUT_ACTIONS = [SET_TIMEOUT_ACTIVE];
    let orderId, klass;

    beforeEach(() => {
      const klasses = generateFakeKlasses(1, {hasPayment: true});
      klass = klasses[0];
      orderId = klass.payments[0].order.id;
      klassesStub = fetchStub
        .withArgs(klassesUrl)
        .returns(Promise.resolve(klasses));
    });

    it('shows the order status toast when the query param is set for a cancellation', () => {
      window.location = '/pay/?status=cancel';
      return renderFullPaymentPage(TOAST_ACTIONS).then(() => {
        assert.deepEqual(store.getState().ui.toastMessage, {
          message: "Order was cancelled",
          icon: TOAST_FAILURE
        });
      });
    });

    it('shows the order status toast when the query param is set for a success', () => {
      window.location = `/pay?status=receipt&order=${orderId}`;
      return renderFullPaymentPage(TOAST_ACTIONS).then(() => {
        assert.deepEqual(store.getState().ui.toastMessage, {
          title: "Payment Complete!",
          icon: TOAST_SUCCESS
        });
      });
    });

    describe('toast loop', () => {
      it("doesn't have a toast message loop on success", () => {
        const customMessage = {
          "message": "Custom toast message was not replaced"
        };
        store.dispatch(setToastMessage(customMessage));
        window.location = `/pay?status=receipt&order=${orderId}`;
        return renderFullPaymentPage().then(() => {
          assert.deepEqual(store.getState().ui.toastMessage, customMessage);
        });
      });

      it("doesn't have a toast message loop on failure", () => {
        const customMessage = {
          "message": "Custom toast message was not replaced"
        };
        store.dispatch(setToastMessage(customMessage));
        window.location = '/dashboard?status=cancel';
        return renderFullPaymentPage().then(() => {
          assert.deepEqual(store.getState().ui.toastMessage, customMessage);
        });
      });
    });

    describe('fake timer tests', function() {
      let clock;
      beforeEach(() => {
        clock = sandbox.useFakeTimers(moment('2016-09-01').valueOf());
      });

      it('refetches the klasses after 3 seconds if 30 seconds has not passed', () => {
        window.location = `/pay?status=receipt&order=missing`;
        return renderFullPaymentPage(TIMEOUT_ACTIONS).then(() => {
          assert.equal(klassesStub.callCount, 1);
          clock.tick(3501);
          assert.equal(klassesStub.callCount, 2);
        });
      });

      it('shows an error message if more than 30 seconds have passed', () => {
        window.location = '/pay?status=receipt&order=missing';
        return renderFullPaymentPage(TIMEOUT_ACTIONS).then(() => {
          let past = moment().add(-125, 'seconds').toISOString();
          store.dispatch(setInitialTime(past));
          clock.tick(3500);
          assert.deepEqual(store.getState().ui.toastMessage, {
            message: `Order was not processed`,
            icon: TOAST_FAILURE
          });
        });
      });
    });
  });
});
