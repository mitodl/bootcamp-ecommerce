import { assert } from "chai"
import moment from "moment"
import _ from "lodash"

import { generateFakeRuns, generateFakeInstallment } from "../factories"
import {
  createForm,
  isNilOrBlank,
  formatDollarAmount,
  getRunWithFulfilledOrder,
  getInstallmentDeadlineDates
} from "./util"

describe("util", () => {
  describe("createForm", () => {
    it("creates a form with hidden values corresponding to the payload", () => {
      const url = "url"
      const payload = { pay: "load" }
      const form = createForm(url, payload)

      const clone = { ...payload }
      for (const hidden of form.querySelectorAll("input[type=hidden]")) {
        const key = hidden.getAttribute("name")
        const value = hidden.getAttribute("value")
        assert.equal(clone[key], value)
        delete clone[key]
      }
      // all keys exhausted
      assert.deepEqual(clone, {})
      assert.equal(form.getAttribute("action"), url)
      assert.equal(form.getAttribute("method"), "post")
    })
  })

  describe("isNilOrBlank", () => {
    it("returns true for undefined, null, and a blank string", () => {
      [undefined, null, ""].forEach(value => {
        assert.isTrue(isNilOrBlank(value))
      })
    })

    it("returns false for a non-blank string", () => {
      assert.isFalse(isNilOrBlank("not blank"))
    })
  })

  describe("formatDollarAmount", () => {
    it("returns a properly formatted dollar value", () => {
      [undefined, null].forEach(nilValue => {
        assert.equal(formatDollarAmount(nilValue), "$0")
      })
      assert.equal(formatDollarAmount(100), "$100")
      assert.equal(formatDollarAmount(100.5), "$100.50")
      assert.equal(formatDollarAmount(10000), "$10,000")
      assert.equal(formatDollarAmount(100.12), "$100.12")
    })
  })

  describe("getRunWithFulfilledOrder", () => {
    let bootcampRuns, bootcampRun

    beforeEach(() => {
      bootcampRuns = generateFakeRuns(1, { hasPayment: true })
      bootcampRun = bootcampRuns[0]
    })

    it("gets a fulfilled order from the payments in the bootcamp runs", () => {
      bootcampRun.payments[0].order.status = "fulfilled"
      assert.deepEqual(
        getRunWithFulfilledOrder(
          bootcampRuns,
          bootcampRun.payments[0].order.id
        ),
        bootcampRun
      )
    })

    it("returns undefined if the order doesn't exist", () => {
      bootcampRun.payments[0].order.status = "fulfilled"
      assert.deepEqual(getRunWithFulfilledOrder(bootcampRuns, 9999), undefined)
    })

    it("returns undefined if the order is not fulfilled", () => {
      bootcampRun.payments[0].order.status = "created"
      assert.deepEqual(
        getRunWithFulfilledOrder(
          bootcampRuns,
          bootcampRun.payments[0].order.id
        ),
        undefined
      )
    })
  })

  describe("getInstallmentDeadlineDates", () => {
    it("returns a list of parsed deadline dates when given an array of installment data", () => {
      const moments = [
        moment({ milliseconds: 0 }),
        moment({ milliseconds: 0 }).add(5, "days")
      ]
      const installments = [
        generateFakeInstallment({ deadline: moments[0].format() }),
        generateFakeInstallment({ deadline: moments[1].format() })
      ]
      // Assert that the arrays of dates are equivalent (using this approach since moment objects
      // store a bunch of extra properties that make assert.deepEqual unusable)
      _.each(getInstallmentDeadlineDates(installments), (installment, i) => {
        assert.isTrue(installment.isSame(moments[i]))
      })
    })
  })
})
