/* global SETTINGS: false */
import React from "react"
import { shallow } from "enzyme"
import { assert } from "chai"
import _ from "lodash"
import moment from "moment"

import Payment from "./Payment"
import { generateFakeRuns, generateFakeInstallment } from "../factories"
import {
  formatDollarAmount,
  formatReadableDate,
  formatReadableDateFromStr
} from "../util/util"

describe("Payment", () => {
  const paymentSectionSelector = ".payment-section"
  const deadlineMsgSelector = ".deadline-message"
  const runDropdownSelector = "select.klass-select"
  const welcomeMsgSelector = "h1.greeting"
  const runTitleSelector = ".klass-display-section .desc"

  const defaultProps = {
    ui:                        {},
    payment:                   {},
    payableBootcampRunsData:   [],
    selectedBootcampRun:       undefined,
    now:                       moment(),
    sendPayment:               () => {},
    setPaymentAmount:          () => {},
    setSelectedBootcampRunKey: () => {}
  }

  const renderPayment = (props = {}) => {
    return shallow(<Payment {...defaultProps} {...props} />)
  }

  it("should show the user a message when no bootcamp runs are eligible for payment", () => {
    const wrapper = renderPayment({ payableBootcampRunsData: [] })
    assert.include(wrapper.html(), "No payment is required at this time.")
  })

  it("shows the name of the user in a welcome message", () => {
    const fakeRuns = generateFakeRuns()
    const wrapper = renderPayment({ payableBootcampRunsData: fakeRuns })
    const welcomeMsg = wrapper.find(welcomeMsgSelector)
    assert.include(welcomeMsg.text(), SETTINGS.user.full_name)
  })

  it("does not show the welcome message if the name of the user is blank", () => {
    SETTINGS.user.full_name = ""
    const fakeRuns = generateFakeRuns()
    const wrapper = renderPayment({ payableBootcampRunsData: fakeRuns })
    assert.isFalse(wrapper.find(welcomeMsgSelector).exists())
  })

  it("shows the selected bootcamp run", () => {
    const fakeRuns = generateFakeRuns(3)
    const wrapper = renderPayment({
      payableBootcampRunsData: fakeRuns,
      selectedBootcampRun:     fakeRuns[0]
    })
    const title = wrapper.find(runTitleSelector)
    assert.include(title.text(), fakeRuns[0].display_title)
  })
  ;[
    [moment().format(), "non-null date message"],
    [null, "null date message"]
  ].forEach(([deadlineDateISO, deadlineDateDesc]) => {
    it(`shows payment due date message with ${deadlineDateDesc}`, () => {
      const fakeRuns = generateFakeRuns(1)
      fakeRuns[0].payment_deadline = deadlineDateISO
      const wrapper = renderPayment({
        payableBootcampRunsData: fakeRuns,
        selectedBootcampRun:     fakeRuns[0]
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
    const fakeRun = generateFakeRuns(1, { hasInstallment: true })[0]
    const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
    const termsText = wrapper.find(".tac").text()
    const termsLink = wrapper.find(".tac-link")

    assert.include(
      termsText,
      "By making a payment I certify that I agree with the MIT Bootcamps Terms and Conditions"
    )
    assert.equal(termsLink.prop("href"), "/terms_and_conditions/")
  })

  describe("bootcamp run dropdown", () => {
    [
      [1, false],
      [2, true]
    ].forEach(([numRuns, shouldShowDropdown]) => {
      it(`should${
        shouldShowDropdown ? "" : " not"
      } be shown when ${numRuns} bootcamp runs available`, () => {
        const fakeRuns = generateFakeRuns(numRuns)
        const wrapper = renderPayment({ payableBootcampRunsData: fakeRuns })
        assert.equal(
          wrapper.find(runDropdownSelector).exists(),
          shouldShowDropdown
        )
      })
    })
  })

  describe('"No payments required" message', () => {
    const noPaymentMsg = "No payment is required at this time"
    ;[
      [0, true],
      [1, false],
      [2, false]
    ].forEach(([numRuns, shouldShowMessage]) => {
      it(`should${
        shouldShowMessage ? "" : " not"
      } be shown when ${numRuns} bootcamp runs available`, () => {
        const fakeRuns = generateFakeRuns(numRuns)
        const wrapper = renderPayment({ payableBootcampRunsData: fakeRuns })
        assert.equal(
          wrapper
            .find(paymentSectionSelector)
            .html()
            .indexOf(noPaymentMsg) >= 0,
          shouldShowMessage
        )
      })
    })
  })

  describe("deadline message", () => {
    it("should show the final payment deadline date and no installment deadline with one installment", () => {
      const fakeRun = generateFakeRuns(1, { hasInstallment: true })[0]
      const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
      const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
      const expectedFinalDeadline = formatReadableDateFromStr(
        fakeRun.installments[0].deadline
      )
      assert.include(
        deadlineMsgHtml,
        `Full payment must be complete by ${expectedFinalDeadline}`
      )
      assert.notInclude(deadlineMsgHtml, "A deposit of")
    })

    it("should show the final payment deadline date with multiple installments", () => {
      const fakeRun = generateFakeRuns(1)[0]
      const future = moment().add(5, "days")
      fakeRun.installments = [
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
      const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
      const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
      assert.include(
        deadlineMsgHtml,
        `Full payment must be complete by ${formatReadableDate(future)}`
      )
    })

    it("should show an installment deadline message when multiple installments exist", () => {
      const fakeRun = generateFakeRuns(1)[0]
      const nextInstallmentDate = moment().add(5, "days")
      fakeRun.installments = [
        generateFakeInstallment({ deadline: nextInstallmentDate.format() }),
        generateFakeInstallment({
          deadline: moment(nextInstallmentDate)
            .add(1, "days")
            .format()
        })
      ]
      const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
      const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
      const installmentAmount = formatDollarAmount(
        fakeRun.installments[0].amount
      )
      assert.include(
        deadlineMsgHtml,
        `A deposit of ${installmentAmount} is due ${formatReadableDate(
          nextInstallmentDate
        )}`
      )
    })

    describe("with multiple past installments", () => {
      const nextInstallmentDate = moment().add(2, "days")
      const amt = 100
      let fakeRun

      beforeEach(() => {
        fakeRun = generateFakeRuns(1)[0]
        fakeRun.installments = [
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
        const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
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
        fakeRun.total_paid = 0
        const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
        assert.include(
          deadlineMsgHtml,
          "You missed the previous payment deadline."
        )
      })

      it('should not show "missed deadline" message if total payment is greater than last installment amount', () => {
        fakeRun.total_paid = amt * 3 - 1
        const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
        assert.notInclude(
          deadlineMsgHtml,
          "You missed the previous payment deadline."
        )
      })

      it("should not show an installment deadline message if the next installment is the last", () => {
        fakeRun.installments = _.slice(
          fakeRun.installments,
          0,
          fakeRun.installments.length - 1
        )
        const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).html()
        assert.notInclude(deadlineMsgHtml, "A deposit of ")
      })

      it("should not show an installment deadline message if there are no installments", () => {
        fakeRun.installments = []
        const wrapper = renderPayment({ selectedBootcampRun: fakeRun })
        const deadlineMsgHtml = wrapper.find(deadlineMsgSelector).text()
        assert.equal(deadlineMsgHtml, "")
      })
    })
  })
})
