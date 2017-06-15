import React from 'react';
import { shallow } from 'enzyme';
import { assert } from 'chai';
import _ from 'lodash';
import moment from 'moment';

import Payment from './Payment';
import {
  generateFakeKlasses,
  generateFakeInstallment
} from '../factories';
import {
  formatDollarAmount,
  formatReadableDate,
  formatReadableDateFromStr
} from '../util/util';

describe("Payment", () => {
  const paymentSectionSelector = '.payment-section',
    deadlineMsgSelector = '.deadline-message',
    klassDropdownSelector = 'select.klass-select';

  let defaultProps = {
    ui: {},
    payment: {},
    payableKlassesData: [],
    selectedKlass: undefined,
    now: moment(),
    sendPayment: () => {},
    setPaymentAmount: () => {},
    setSelectedKlassKey: () => {}
  };

  let renderPayment = (props = {}) => {
    return shallow(
      <Payment {...defaultProps} {...props} />
    );
  };

  it('should show the user a message when no klasses are eligible for payment', () => {
    let wrapper = renderPayment({payableKlassesData: []});
    assert.include(wrapper.html(), 'No payment is required at this time.');
  });

  describe('klass dropdown', () => {
    [
      [1, false],
      [2, true]
    ].forEach(([numKlasses, shouldShowDropdown]) => {
      it(`should${shouldShowDropdown ? '' : ' not'} be shown when ${numKlasses} klasses available`, () => {
        let fakeKlasses = generateFakeKlasses(numKlasses);
        let wrapper = renderPayment({payableKlassesData: fakeKlasses});
        assert.equal(wrapper.find(klassDropdownSelector).exists(), shouldShowDropdown);
      });
    });
  });

  describe('"No payments required" message', () => {
    let noPaymentMsg = "No payment is required at this time";
    [
      [0, true],
      [1, false],
      [2, false]
    ].forEach(([numKlasses, shouldShowMessage]) => {
      it(`should${shouldShowMessage ? '' : ' not'} be shown when ${numKlasses} klasses available`, () => {
        let fakeKlasses = generateFakeKlasses(numKlasses);
        let wrapper = renderPayment({payableKlassesData: fakeKlasses});
        assert.equal(wrapper.find(paymentSectionSelector).html().indexOf(noPaymentMsg) >= 0, shouldShowMessage);
      });
    });
  });


  describe('deadline message', () => {
    it('should show the final payment deadline date and no installment deadline with one installment', () => {
      let fakeKlass = generateFakeKlasses(1, {hasInstallment: true})[0];
      let wrapper = renderPayment({selectedKlass: fakeKlass});
      let deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html();
      let expectedFinalDeadline = formatReadableDateFromStr(fakeKlass.installments[0].deadline);
      assert.include(deadlineMsgHtml, `Full payment must be complete by ${expectedFinalDeadline}`);
      assert.notInclude(deadlineMsgHtml, 'A deposit of');
    });

    it('should show the final payment deadline date with multiple installments', () => {
      let fakeKlass = generateFakeKlasses(1)[0];
      let future = moment().add(5, 'days');
      fakeKlass.installments = [
        generateFakeInstallment({deadline: moment(future).add(-2, 'days').format()}),
        generateFakeInstallment({deadline: moment(future).add(-1, 'days').format()}),
        generateFakeInstallment({deadline: future.format()})
      ];
      let wrapper = renderPayment({selectedKlass: fakeKlass});
      let deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html();
      assert.include(deadlineMsgHtml, `Full payment must be complete by ${formatReadableDate(future)}`);
    });

    it('should show an installment deadline message when multiple installments exist', () => {
      let fakeKlass = generateFakeKlasses(1)[0];
      let nextInstallmentDate = moment().add(5, 'days');
      fakeKlass.installments = [
        generateFakeInstallment({deadline: nextInstallmentDate.format()}),
        generateFakeInstallment({deadline: moment(nextInstallmentDate).add(1, 'days').format()})
      ];
      let wrapper = renderPayment({selectedKlass: fakeKlass});
      let deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html();
      let installmentAmount = formatDollarAmount(fakeKlass.installments[0].amount);
      assert.include(
        deadlineMsgHtml,
        `A deposit of ${installmentAmount} is due ${formatReadableDate(nextInstallmentDate)}`
      );
    });

    describe('with multiple past installments', () => {
      const nextInstallmentDate = moment().add(2, 'days'),
        amt = 100;
      let fakeKlass;

      beforeEach(() => {
        fakeKlass = generateFakeKlasses(1)[0];
        fakeKlass.installments = [
          generateFakeInstallment({deadline: moment(nextInstallmentDate).add(-9, 'days').format(), amount: amt}),
          generateFakeInstallment({deadline: moment(nextInstallmentDate).add(-8, 'days').format(), amount: amt}),
          generateFakeInstallment({deadline: nextInstallmentDate.format(), amount: amt}),
          generateFakeInstallment({deadline: moment(nextInstallmentDate).add(1, 'days').format(), amount: amt})
        ];
      });

      it('should show a sum of installment amounts', () => {
        let wrapper = renderPayment({selectedKlass: fakeKlass});
        let deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html();
        let installmentAmount = formatDollarAmount(amt * 3);
        assert.include(
          deadlineMsgHtml,
          `A deposit of ${installmentAmount} is due ${formatReadableDate(nextInstallmentDate)}`
        );
      });

      it('should show "missed deadline" message if total payment is less than the last installment amount', () => {
        fakeKlass.total_paid = 0;
        let wrapper = renderPayment({selectedKlass: fakeKlass});
        let deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html();
        assert.include(deadlineMsgHtml, 'You missed the previous payment deadline.');
      });

      it('should not show "missed deadline" message if total payment is greater than last installment amount', () => {
        fakeKlass.total_paid = (amt * 3) - 1;
        let wrapper = renderPayment({selectedKlass: fakeKlass});
        let deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html();
        assert.notInclude(deadlineMsgHtml, 'You missed the previous payment deadline.');
      });

      it('should not show an installment deadline message if the next installment is the last', () => {
        fakeKlass.installments = _.slice(fakeKlass.installments, 0, fakeKlass.installments.length - 1);
        let wrapper = renderPayment({selectedKlass: fakeKlass});
        let deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html();
        assert.notInclude(deadlineMsgHtml, 'A deposit of ');
      });
    });
  });
});
