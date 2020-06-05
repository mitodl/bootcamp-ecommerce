// @flow
import { assert } from "chai"
import moment from "moment"
import sinon from "sinon"

import PaymentDisplay, {
  PaymentDisplay as InnerPaymentDisplay
} from "./PaymentDisplay"

import IntegrationTestHelper from "../util/integration_test_helper"
import { PAYMENT } from "../constants"
import { makeApplicationDetail } from "../factories/application"
import * as util from "../util/util"
import wait from "waait"

describe("PaymentDisplay", () => {
  let helper, renderPage, application

  beforeEach(() => {
    application = makeApplicationDetail()
    helper = new IntegrationTestHelper()
    renderPage = helper.configureHOCRenderer(
      PaymentDisplay,
      InnerPaymentDisplay,
      {
        drawer: {
          drawerOpen:  true,
          drawerState: PAYMENT,
          drawerMeta:  {
            applicationId: application.id
          }
        },
        entities: {
          applicationDetail: {
            [application.id]: application
          }
        }
      }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders nothing if there is no application (yet)", async () => {
    const { inner } = await renderPage({
      entities: { applicationDetail: null }
    })
    assert.isNull(inner.html())
  })

  it("renders the bootcamp title", async () => {
    const { inner } = await renderPage()
    assert.equal(
      inner.find(".bootcamp-title").text(),
      application.bootcamp_run.bootcamp.title
    )
  })

  const TEST_DATE = "2020-05-01"
  describe("start and end dates", () => {
    [
      [
        moment(TEST_DATE).format(),
        moment(TEST_DATE)
          .add(1, "days")
          .format(),
        "mai 1, 2020 - mai 2, 2020"
      ],
      [moment(TEST_DATE).format(), null, "mai 1, 2020 - TBD"],
      [
        null,
        moment(TEST_DATE)
          .add(1, "days")
          .format(),
        "TBD - mai 2, 2020"
      ],
      [null, null, "TBD - TBD"]
    ].forEach(([startDate, endDate, expectedText]) => {
      it(`renders bootcamp dates where startDate=${String(
        startDate
      )} and endDate=${String(endDate)}`, async () => {
        application.bootcamp_run.start_date = startDate
        application.bootcamp_run.end_date = endDate
        const { inner } = await renderPage()
        assert.equal(inner.find(".bootcamp-dates").text(), expectedText)
      })
    })
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
    it("does nothing if the payment textbox is empty", async () => {
      const { inner } = await renderPage()
      inner.find(".payment-input-container input").prop("onChange")({
        target: { value: "" }
      })
      inner.find(".payment-input-container button").prop("onClick")()
    })

    it("does nothing if the payment textbox is not parseable as a float", async () => {
      const { inner } = await renderPage()
      inner.find(".payment-input-container input").prop("onChange")({
        target: { value: "🦀🦀🦀🦀🦀🦀🦀🦀" }
      })
      inner.find(".payment-input-container button").prop("onClick")()
    })

    it("does nothing if the amount is 0", async () => {
      const { inner } = await renderPage()
      inner.find(".payment-input-container input").prop("onChange")({
        target: { value: "0.00000001" } // rounds to 0
      })
      inner.find(".payment-input-container button").prop("onClick")()
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

      const { inner } = await renderPage()
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
      inner.find(".payment-input-container input").prop("onChange")({
        target: { value: payment }
      })
      inner.find(".payment-input-container button").prop("onClick")()

      await wait(50)
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
            payment_amount: "123.46"
          },
          credentials: undefined,
          headers:     { "X-CSRFTOKEN": null }
        }
      )
    })
  })
})
