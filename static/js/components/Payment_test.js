/* global SETTINGS: false */
import React from "react"
import { shallow } from "enzyme"
import { assert } from "chai"
import _ from "lodash"
import moment from "moment"

import Payment from "./Payment"
import { generateFakeKlasses, generateFakeInstallment } from "../factories"
import {
  formatDollarAmount,
  formatReadableDate,
  formatReadableDateFromStr
} from "../util/util"

describe("Payment", () => {
  const paymentSectionSelector = ".payment-section",
    deadlineMsgSelector = ".deadline-message",
    klassDropdownSelector = "select.klass-select",
    welcomeMsgSelector = "h1.greeting",
    klassTitleSelector = ".klass-display-section .desc"

  const defaultProps = {
    ui:                  {},
    payment:             {},
    payableKlassesData:  [],
    selectedKlass:       undefined,
    now:                 moment(),
    sendPayment:         () => {},
    setPaymentAmount:    () => {},
    setSelectedKlassKey: () => {}
  }

  const renderPayment = (props = {}) => {
    return shallow(<Payment {...defaultProps} {...props} />)
  }

  it("should show the user a message when no klasses are eligible for payment", () => {
    const wrapper = renderPayment({ payableKlassesData: [] })
    assert.include(wrapper.html(), "No payment is required at this time.")
  })

  it("shows the name of the user in a welcome message", () => {
    const fakeKlasses = generateFakeKlasses()
    const wrapper = renderPayment({ payableKlassesData: fakeKlasses })
    const welcomeMsg = wrapper.find(welcomeMsgSelector)
    assert.include(welcomeMsg.text(), SETTINGS.user.full_name)
  })

  it("does not show the welcome message if the name of the user is blank", () => {
    SETTINGS.user.full_name = ""
    const fakeKlasses = generateFakeKlasses()
    const wrapper = renderPayment({ payableKlassesData: fakeKlasses })
    assert.isFalse(wrapper.find(welcomeMsgSelector).exists())
  })

  it("shows the selected klass", () => {
    const fakeKlasses = generateFakeKlasses(3)
    const wrapper = renderPayment({
      payableKlassesData: fakeKlasses,
      selectedKlass:      fakeKlasses[0]
    })
    const title = wrapper.find(klassTitleSelector)
    assert.include(title.text(), fakeKlasses[0].display_title)
  })
  ;[
    [moment().format(), "non-null date message"],
    [null, "null date message"]
  ].forEach(([deadlineDateISO, deadlineDateDesc]) => {
    it(`shows payment due date message with ${deadlineDateDesc}`, () => {
      const fakeKlasses = generateFakeKlasses(1)
      fakeKlasses[0].payment_deadline = deadlineDateISO
      const wrapper = renderPayment({
        payableKlassesData: fakeKlasses,
        selectedKlass:      fakeKlasses[0]
      })
      const deadlineText = wrapper.find(deadlineMsgSelector).text()
      if (!_.isEmpty(deadlineDateISO)) {
        assert.include(
          deadlineText,
          formatReadableDate(moment(deadlineDateISO))
        )
      }
    })
  })

  it("should show terms and conditions message", () => {
    const fakeKlass = generateFakeKlasses(1, { hasInstallment: true })[0]
    const wrapper = renderPayment({ selectedKlass: fakeKlass })
    const termsText = wrapper.find(".tac").text()
    const termsLink = wrapper.find(".tac-link")

    assert.include(
      termsText,
      "By making a payment I certify that I agree with the MIT Bootcamps Terms and Conditions"
    )
    assert.equal(termsLink.prop("href"), "/terms_and_conditions/")
  })

  describe("klass dropdown", () => {
    [[1, false], [2, true]].forEach(([numKlasses, shouldShowDropdown]) => {
      it(`should${
        shouldShowDropdown ? "" : " not"
      } be shown when ${numKlasses} klasses available`, () => {
        const fakeKlasses = generateFakeKlasses(numKlasses)
        const wrapper = renderPayment({ payableKlassesData: fakeKlasses })
        assert.equal(
          wrapper.find(klassDropdownSelector).exists(),
          shouldShowDropdown
        )
      })
    })
  })

  describe('"No payments required" message', () => {
    const noPaymentMsg = "No payment is required at this time"
    ;[[0, true], [1, false], [2, false]].forEach(
      ([numKlasses, shouldShowMessage]) => {
        it(`should${
          shouldShowMessage ? "" : " not"
        } be shown when ${numKlasses} klasses available`, () => {
          const fakeKlasses = generateFakeKlasses(numKlasses)
          const wrapper = renderPayment({ payableKlassesData: fakeKlasses })
          assert.equal(
            wrapper
              .find(paymentSectionSelector)
              .html()
              .indexOf(noPaymentMsg) >= 0,
            shouldShowMessage
          )
        })
      }
    )
  })

  describe("deadline message", () => {
    it("should show the final payment deadline date and no installment deadline with one installment", () => {
      const fakeKlass = generateFakeKlasses(1, { hasInstallment: true })[0]
      const wrapper = renderPayment({ selectedKlass: fakeKlass })
      const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
      const expectedFinalDeadline = formatReadableDateFromStr(
        fakeKlass.installments[0].deadline
      )
      assert.include(
        deadlineMsgHtml,
        `Full payment must be complete by ${expectedFinalDeadline}`
      )
      assert.notInclude(deadlineMsgHtml, "A deposit of")
    })

    it("should show the final payment deadline date with multiple installments", () => {
      const fakeKlass = generateFakeKlasses(1)[0]
      const future = moment().add(5, "days")
      fakeKlass.installments = [
        generateFakeInstallment({
          deadline: moment(future)
            .add(-2, "days")
            .format()
        }),
        generateFakeInstallment({
          deadline: moment(future)
            .add(-1, "days")
            .format()
        }),
        generateFakeInstallment({ deadline: future.format() })
      ]
      const wrapper = renderPayment({ selectedKlass: fakeKlass })
      const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
      assert.include(
        deadlineMsgHtml,
        `Full payment must be complete by ${formatReadableDate(future)}`
      )
    })

    it("should show an installment deadline message when multiple installments exist", () => {
      const fakeKlass = generateFakeKlasses(1)[0]
      const nextInstallmentDate = moment().add(5, "days")
      fakeKlass.installments = [
        generateFakeInstallment({ deadline: nextInstallmentDate.format() }),
        generateFakeInstallment({
          deadline: moment(nextInstallmentDate)
            .add(1, "days")
            .format()
        })
      ]
      const wrapper = renderPayment({ selectedKlass: fakeKlass })
      const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
      const installmentAmount = formatDollarAmount(
        fakeKlass.installments[0].amount
      )
      assert.include(
        deadlineMsgHtml,
        `A deposit of ${installmentAmount} is due ${formatReadableDate(
          nextInstallmentDate
        )}`
      )
    })

    describe("with multiple past installments", () => {
      const nextInstallmentDate = moment().add(2, "days"),
        amt = 100
      let fakeKlass

      beforeEach(() => {
        fakeKlass = generateFakeKlasses(1)[0]
        fakeKlass.installments = [
          generateFakeInstallment({
            deadline: moment(nextInstallmentDate)
              .add(-9, "days")
              .format(),
            amount: amt
          }),
          generateFakeInstallment({
            deadline: moment(nextInstallmentDate)
              .add(-8, "days")
              .format(),
            amount: amt
          }),
          generateFakeInstallment({
            deadline: nextInstallmentDate.format(),
            amount:   amt
          }),
          generateFakeInstallment({
            deadline: moment(nextInstallmentDate)
              .add(1, "days")
              .format(),
            amount: amt
          })
        ]
      })

      it("should show a sum of installment amounts", () => {
        const wrapper = renderPayment({ selectedKlass: fakeKlass })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
        const installmentAmount = formatDollarAmount(amt * 3)
        assert.include(
          deadlineMsgHtml,
          `A deposit of ${installmentAmount} is due ${formatReadableDate(
            nextInstallmentDate
          )}`
        )
      })

      it('should show "missed deadline" message if total payment is less than the last installment amount', () => {
        fakeKlass.total_paid = 0
        const wrapper = renderPayment({ selectedKlass: fakeKlass })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
        assert.include(
          deadlineMsgHtml,
          "You missed the previous payment deadline."
        )
      })

      it('should not show "missed deadline" message if total payment is greater than last installment amount', () => {
        fakeKlass.total_paid = amt * 3 - 1
        const wrapper = renderPayment({ selectedKlass: fakeKlass })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
        assert.notInclude(
          deadlineMsgHtml,
          "You missed the previous payment deadline."
        )
      })

      it("should not show an installment deadline message if the next installment is the last", () => {
        fakeKlass.installments = _.slice(
          fakeKlass.installments,
          0,
          fakeKlass.installments.length - 1
        )
        const wrapper = renderPayment({ selectedKlass: fakeKlass })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
        assert.notInclude(deadlineMsgHtml, "A deposit of ")
      })

      it("should not show an installment deadline message if there are no installments", () => {
        fakeKlass.installments = []
        const wrapper = renderPayment({ selectedKlass: fakeKlass })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).text()
        assert.equal(deadlineMsgHtml, "")
      })
    })
  })
})
