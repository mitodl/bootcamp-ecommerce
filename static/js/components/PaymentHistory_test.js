import React from "react"
import { shallow } from "enzyme"
import { assert } from "chai"
import _ from "lodash"

import PaymentHistory from "./PaymentHistory"
import { generateFakeKlasses } from "../factories"

describe("PaymentHistory", () => {
  const statementLinkSelector = "a.statement-link"

  const renderPaymentHistory = klassDataWithPayments =>
    shallow(<PaymentHistory klassDataWithPayments={klassDataWithPayments} />)

  const setPaymentValues = (klassesData, paymentAmount) =>
    _.map(klassesData, klass => _.set(klass, "total_paid", paymentAmount))

  it("should show rows of payment history information", () => {
    const klassCount = 3
    const paymentAmount = 100
    let fakeKlasses = generateFakeKlasses(klassCount)
    // Set all fake klasses to have payments
    fakeKlasses = setPaymentValues(fakeKlasses, paymentAmount)
    fakeKlasses[0].price = 1000
    fakeKlasses[1].price = paymentAmount

    const wrapper = renderPaymentHistory(fakeKlasses)
    const paymentHistoryTableRows = wrapper.find("tbody tr")
    assert.equal(paymentHistoryTableRows.length, klassCount)
    const firstRowHtml = paymentHistoryTableRows.at(0).html()
    assert.include(firstRowHtml, fakeKlasses[0].display_title)
    assert.include(firstRowHtml, `$${paymentAmount} out of $1,000`)
    const secondRowHtml = paymentHistoryTableRows.at(1).html()
    assert.include(secondRowHtml, fakeKlasses[1].display_title)
    assert.include(secondRowHtml, `$${paymentAmount}`)
  })

  it("should show a link to view a payment statement", () => {
    const fakeKlasses = generateFakeKlasses(1)
    const wrapper = renderPaymentHistory(fakeKlasses)
    const statementLink = wrapper.find(statementLinkSelector)
    assert.equal(
      statementLink.prop("href"),
      `/statement/${fakeKlasses[0].klass_key}`
    )
  })
})
