// @flow
import { assert } from "chai"
import sinon from "sinon"
import { Field } from "formik"
import { shallow } from "enzyme"

import PaymentDisplay, {
  PaymentDisplay as InnerPaymentDisplay
} from "./PaymentDisplay"

import { makeApplicationDetail } from "../factories/application"
import IntegrationTestHelper from "../util/integration_test_helper"
import * as util from "../util/util"

describe("PaymentDisplay", () => {
  let helper, renderPage, application

  beforeEach(() => {
    application = makeApplicationDetail()
    helper = new IntegrationTestHelper()
    renderPage = helper.configureHOCRenderer(
      PaymentDisplay,
      InnerPaymentDisplay,
      {},
      { application: application }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders nothing if there is no application (yet)", async () => {
    const { inner } = await renderPage({}, { application: null })
    assert.isNull(inner.html())
  })

  it("renders the bootcamp title", async () => {
    const { inner } = await renderPage()
    assert.equal(
      inner.find(".bootcamp-title").text(),
      application.bootcamp_run.bootcamp.title
    )
  })

  it("renders bootcamp dates", async () => {
    const dateRangeText = "date range text"
    const rangeStub = helper.sandbox
      .stub(util, "formatRunDateRange")
      .returns(dateRangeText)
    const { inner } = await renderPage()
    assert.equal(inner.find(".bootcamp-dates").text(), dateRangeText)
    sinon.assert.calledWith(rangeStub, application.bootcamp_run)
  })

  it("should show the final payment deadline", async () => {
    application.payment_deadline = "2020-02-21"
    const { inner } = await renderPage()
    assert.equal(
      inner.find(".payment-deadline").text(),
      "Full payment must be complete by febr. 21, 2020"
    )
  })

  it("should show the amount paid so far", async () => {
    application.price = 123.456
    // $FlowFixMe
    application.orders = [{ total_price_paid: 20 }, { total_price_paid: 30 }]
    const { inner } = await renderPage()
    assert.equal(
      inner.find(".payment-amount").text(),
      "You have paid $50 out of $123.46."
    )
  })

  describe("submitting payment", () => {
    const renderFormik = async (...args) => {
      const { inner } = await renderPage(...args)
      const formik = inner.find("Formik")
      const rendered = shallow(formik.prop("render")({})).dive()
      return { formik, inner: rendered }
    }

    it("does nothing if the payment textbox is empty", async () => {
      const { inner } = await renderFormik()
      assert.deepEqual(
        inner
          .find(Field)
          .filter("[name='amount']")
          .prop("validate")(""),
        "Price must be a valid number"
      )
    })

    it("does nothing if the payment textbox is not parseable as a float", async () => {
      const { inner } = await renderFormik()
      assert.deepEqual(
        inner
          .find(Field)
          .filter("[name='amount']")
          .prop("validate")("abc"),
        "Price must be a valid number"
      )
    })

    it("does nothing if the amount is 0", async () => {
      const { inner } = await renderFormik()
      assert.deepEqual(
        inner
          .find(Field)
          .filter("[name='amount']")
          .prop("validate")("0.000001"),
        "Price must be greater than zero"
      )
    })

    it("sends a payment", async () => {
      const submitStub = helper.sandbox.stub()
      const fakeForm = document.createElement("form")
      fakeForm.setAttribute("class", "fake-form")
      // $FlowFixMe
      fakeForm.submit = submitStub
      const createFormStub = helper.sandbox
        .stub(util, "createForm")
        .returns(fakeForm)

      const { formik } = await renderFormik()
      const url = "url"
      const payload = { pay: "load" }
      helper.handleRequestStub.withArgs("/api/v0/payment/").returns({
        status: 200,
        body:   {
          url,
          payload
        }
      })
      const payment = "123.456" // will get rounded to 123.46
      const setSubmittingStub = helper.sandbox.stub()
      await formik.prop("onSubmit")(
        { amount: payment },
        { setSubmitting: setSubmittingStub }
      )

      assert.equal(createFormStub.callCount, 1)
      assert.deepEqual(createFormStub.args[0], [url, payload])
      assert.equal(submitStub.callCount, 1)
      assert.deepEqual(submitStub.args[0], [])
      sinon.assert.calledWith(
        helper.handleRequestStub.withArgs("/api/v0/payment/"),
        "/api/v0/payment/",
        "POST",
        {
          body: {
            application_id: application.id,
            payment_amount: 123.46
          },
          credentials: undefined,
          headers:     { "X-CSRFTOKEN": null }
        }
      )
    })
  })
})
