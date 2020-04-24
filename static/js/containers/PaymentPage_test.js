/* global SETTINGS: false */
import { assert } from "chai"
import moment from "moment"
import wait from "waait"

import { TOAST_SUCCESS, TOAST_FAILURE } from "../constants"
import PaymentPage, { PaymentPage as InnerPaymentPage } from "./PaymentPage"
import { PAYMENT_CONFIRMATION_DIALOG } from "../components/Payment"
import * as util from "../util/util"
import { generateFakeKlasses } from "../factories"
import IntegrationTestHelper from "../util/integration_test_helper"

describe("PaymentPage", () => {
  const paymentInputSelector = 'input[id="payment-amount"]'
  const paymentBtnSelector = "button.large-cta"

  let helper, klassesUrl, fakeKlasses, renderPage

  beforeEach(() => {
    helper = new IntegrationTestHelper()

    SETTINGS.user = {
      full_name: "john doe",
      username:  "johndoe"
    }
    klassesUrl = `/api/v0/klasses/${SETTINGS.user.username}/`
    fakeKlasses = generateFakeKlasses(3, {
      hasInstallment: true,
      hasPayment:     true
    })

    renderPage = helper.configureHOCRenderer(
      PaymentPage,
      InnerPaymentPage,
      {
        entities: {
          klasses: fakeKlasses,
          payment: null
        },
        queries: {
          klasses: {
            isPending:  false,
            isFinished: true
          },
          payment: {
            isPending:  false,
            isFinished: true
          }
        }
      },
      {}
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("does not have a selected klass by default", async () => {
    const { wrapper } = await renderPage()
    assert.isUndefined(wrapper.find("PaymentPage").prop("selectedKlass"))
  })

  it("sets a selected klass", async () => {
    const { inner } = await renderPage({
      ui: {
        selectedKlassKey: 3
      }
    })

    assert.deepEqual(
      inner.find("Payment").prop("selectedKlass"),
      fakeKlasses[2]
    )
  })

  it("only passes payable fakeKlasses to the Payment component", async () => {
    fakeKlasses[1].is_user_eligible_to_pay = false

    const { inner } = await renderPage()
    assert.lengthOf(inner.find("Payment").prop("payableKlassesData"), 2)
  })

  it("does not show the payment & payment history sections while API results are still pending", async () => {
    const { wrapper } = await renderPage({
      queries: {
        payment: {
          isPending:  true,
          isFinished: false
        }
      }
    })

    assert.isFalse(wrapper.find("Payment").exists())
    assert.isFalse(wrapper.find("PaymentHistory").exists())
  })

  //
  ;[
    [100, true, "past payments should"],
    [0, false, "no past payments should not"]
  ].forEach(([totalPaid, shouldShowPayHistory, testDescription]) => {
    it(`for user with ${testDescription} include payment history component`, async () => {
      for (const klass of fakeKlasses) {
        klass.total_paid = totalPaid
      }

      const { inner } = await renderPage()

      assert.equal(inner.find("PaymentHistory").exists(), shouldShowPayHistory)
    })
  })

  describe("payment functionality", () => {
    it("when user overpay", async () => {
      const { inner } = await renderPage({
        ui: {
          selectedKlassKey: 1,
          dialogVisibility: {
            [PAYMENT_CONFIRMATION_DIALOG]: true
          },
          paymentAmount: "2000"
        }
      })

      assert.equal(
        inner
          .find("Payment")
          .dive()
          .find("OurDialog")
          .prop("title"),
        "Confirm Payment"
      )
      assert.equal(
        inner
          .find("Payment")
          .dive()
          .find("OurDialog")
          .find(".overpay-confirm")
          .text(),
        "Are you sure you want to pay $2,000?"
      )
    })

    it("sets a price", async () => {
      const { inner, store } = await renderPage({
        ui: {
          selectedKlassKey: fakeKlasses[1].klass_key
        }
      })
      inner
        .find("Payment")
        .dive()
        .find(paymentInputSelector)
        .props()
        .onChange({
          target: {
            value: "123"
          }
        })
      assert.equal(store.getState().ui.paymentAmount, "123")
    })
  })

  it("constructs a form to be sent to Cybersource and submits it", async () => {
    const url = "/x/y/z"
    const payload = {
      pay: "load"
    }
    helper.handleRequestStub.withArgs("/api/v0/payment/").returns({
      status: 200,
      body:   {
        url,
        payload
      }
    })

    const submitStub = helper.sandbox.stub()
    const fakeForm = document.createElement("form")
    fakeForm.setAttribute("class", "fake-form")
    fakeForm.submit = submitStub
    const createFormStub = helper.sandbox
      .stub(util, "createForm")
      .returns(fakeForm)

    const { inner } = await renderPage({
      ui: {
        paymentAmount:    "123",
        selectedKlassKey: fakeKlasses[1].klass_key
      }
    })
    inner
      .find("Payment")
      .dive()
      .find(paymentBtnSelector)
      .prop("onClick")()

    await wait(50)
    assert.equal(createFormStub.callCount, 1)
    assert.deepEqual(createFormStub.args[0], [url, payload])

    assert(
      document.body.querySelector(".fake-form"),
      "fake form not found in body"
    )
    assert.equal(submitStub.callCount, 1)
    assert.deepEqual(submitStub.args[0], [])
  })

  describe("order receipt and cancellation pages", () => {
    let orderId

    beforeEach(() => {
      orderId = fakeKlasses[0].payments[0].order.id
    })

    it("shows the order status toast when the query param is set for a cancellation", async () => {
      window.location = "/pay/?status=cancel"
      const { store } = await renderPage()
      assert.deepEqual(store.getState().ui.toastMessage, {
        message: "Order was cancelled",
        icon:    TOAST_FAILURE
      })
    })

    it("shows the order status toast when query param is set for a success", async () => {
      window.location = `/pay?status=receipt&order=${orderId}`
      const { store } = await renderPage()
      assert.deepEqual(store.getState().ui.toastMessage, {
        title: "Payment Complete!",
        icon:  TOAST_SUCCESS
      })
    })

    describe("toast loop", () => {
      it("doesn't have a toast message loop on success", async () => {
        const customMessage = {
          message: "Custom toast message was not replaced"
        }
        window.location = `/pay?status=receipt&order=${orderId}`
        const { store } = await renderPage({
          ui: {
            toastMessage: customMessage
          }
        })
        assert.deepEqual(store.getState().ui.toastMessage, customMessage)
      })

      it("doesn't have a toast message loop on failure", async () => {
        const customMessage = {
          message: "Custom toast message was not replaced"
        }
        window.location = "/dashboard?status=cancel"
        const { store } = await renderPage({
          ui: {
            toastMessage: customMessage
          }
        })
        assert.deepEqual(store.getState().ui.toastMessage, customMessage)
      })
    })

    describe("fake timer tests", function() {
      let clock, url, payload
      beforeEach(() => {
        clock = helper.sandbox.useFakeTimers(moment("2016-09-01").valueOf())
        url = "/x/y/z"
        payload = {
          pay: "load"
        }

        helper.handleRequestStub.withArgs("/api/v0/payment/").returns({
          status: 200,
          body:   {
            url,
            payload
          }
        })
      })

      it("refetches the fakeKlasses after 3 seconds if 30 seconds has not passed", async () => {
        window.location = `/pay?status=receipt&order=missing`
        await renderPage()
        assert.equal(helper.handleRequestStub.withArgs(klassesUrl).callCount, 1)
        clock.tick(3501)
        assert.equal(helper.handleRequestStub.withArgs(klassesUrl).callCount, 2)
      })

      it("shows an error message if more than 30 seconds have passed", async () => {
        window.location = "/pay?status=receipt&order=missing"
        const { store, inner } = await renderPage({
          ui: { initialTime: moment().toISOString() }
        })
        inner.setProps({
          ui: {
            initialTime: moment()
              .add(-125, "seconds")
              .toISOString()
          }
        })
        clock.tick(3500)
        assert.deepEqual(store.getState().ui.toastMessage, {
          message: `Order was not processed`,
          icon:    TOAST_FAILURE
        })
      })
    })
  })
})
