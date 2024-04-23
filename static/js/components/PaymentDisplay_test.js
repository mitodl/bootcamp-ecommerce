// @flow
/* global SETTINGS: false */
import { assert } from "chai";
import sinon from "sinon";
import { shallow } from "enzyme";

import PaymentDisplay, {
  PaymentDisplay as InnerPaymentDisplay,
} from "./PaymentDisplay";
import { paymentAPI } from "../lib/urls";

import { makeApplicationDetail } from "../factories/application";
import IntegrationTestHelper from "../util/integration_test_helper";
import * as util from "../util/util";

describe("PaymentDisplay", () => {
  let helper, renderPage, application;

  beforeEach(() => {
    application = makeApplicationDetail();
    helper = new IntegrationTestHelper();
    renderPage = helper.configureHOCRenderer(
      PaymentDisplay,
      InnerPaymentDisplay,
      {},
      { application: application },
    );
  });

  afterEach(() => {
    helper.cleanup();
  });

  it("renders nothing if there is no application (yet)", async () => {
    const { inner } = await renderPage({}, { application: null });
    assert.isNull(inner.html());
  });

  it("renders the bootcamp title", async () => {
    const { inner } = await renderPage();
    assert.equal(
      inner.find(".bootcamp-title").text(),
      application.bootcamp_run.bootcamp.title,
    );
  });

  it("renders the terms and conditions link", async () => {
    SETTINGS.terms_url = "/terms-of-service";
    const { inner } = await renderPage();
    assert.equal(
      inner.find(".terms-and-conditions").find("a").prop("href"),
      SETTINGS.terms_url,
    );
  });

  it("renders bootcamp dates", async () => {
    const dateRangeText = "date range text";
    const rangeStub = helper.sandbox
      .stub(util, "formatRunDateRange")
      .returns(dateRangeText);
    const { inner } = await renderPage();
    assert.equal(inner.find(".bootcamp-dates").text(), dateRangeText);
    sinon.assert.calledWith(rangeStub, application.bootcamp_run);
  });

  it("should show the final payment deadline", async () => {
    application.payment_deadline = "2020-02-21";
    const { inner } = await renderPage();
    assert.equal(
      inner.find(".payment-deadline").text(),
      "Full payment must be complete by feb. 21, 2020",
    );
  });

  it("should show the amount paid so far", async () => {
    application.price = 123.456;
    // $FlowFixMe
    application.orders = [{ total_price_paid: 20 }, { total_price_paid: 30 }];
    const { inner } = await renderPage();
    assert.equal(
      inner.find(".payment-amount").text(),
      "You have paid $50 out of $123.46.",
    );
  });

  describe("submitting payment", () => {
    const renderFormik = async (...args) => {
      const { inner } = await renderPage(...args);
      const formik = inner.find("Formik");
      const rendered = shallow(formik.prop("render")({})).dive();
      return { formik, inner: rendered };
    };

    it("returns a validation error if the payment textbox is empty", async () => {
      const { formik } = await renderFormik();
      assert.deepEqual(
        formik.prop("validate")({
          amount: "",
          balance: 100,
        }),
        { amount: "Payment amount is required" },
      );
    });

    it("returns a validation error if the payment textbox is not parseable as a float", async () => {
      const { formik } = await renderFormik();
      assert.deepEqual(
        formik.prop("validate")({
          amount: "abc",
          balance: 100,
        }),
        { amount: "Payment amount must be a valid number" },
      );
    });
    ["0", "-5"].forEach((amount) => {
      it(`returns a validation error if the amount is ${amount}`, async () => {
        const { formik } = await renderFormik();
        assert.deepEqual(
          formik.prop("validate")({
            amount: String(amount),
            balance: 100,
          }),
          { amount: "Payment amount must be greater than zero" },
        );
      });
    });

    it("returns a validation error if the amount is greater than the balance", async () => {
      const { formik } = await renderFormik();
      assert.deepEqual(
        formik.prop("validate")({
          amount: "105",
          balance: 100,
        }),
        { amount: "Payment amount must be less than the remaining balance" },
      );
    });

    it("sends a payment", async () => {
      const submitStub = helper.sandbox.stub();
      const fakeForm = document.createElement("form");
      fakeForm.setAttribute("class", "fake-form");
      // $FlowFixMe
      fakeForm.submit = submitStub;
      const createFormStub = helper.sandbox
        .stub(util, "createForm")
        .returns(fakeForm);

      const { formik } = await renderFormik();
      const url = "url";
      const payload = { pay: "load" };
      helper.handleRequestStub.withArgs(paymentAPI.toString()).returns({
        status: 200,
        body: {
          url,
          payload,
        },
      });
      const payment = "123.456"; // will get rounded to 123.46
      const resetFormStub = helper.sandbox.stub();
      await formik.prop("onSubmit")(
        { amount: payment },
        { resetForm: resetFormStub },
      );

      sinon.assert.calledOnce(createFormStub);
      sinon.assert.calledOnce(submitStub);
      sinon.assert.calledOnce(resetFormStub);
      sinon.assert.calledWith(
        helper.handleRequestStub.withArgs(paymentAPI.toString()),
        paymentAPI.toString(),
        "POST",
        {
          body: {
            application_id: application.id,
            payment_amount: 123.46,
          },
          credentials: undefined,
          headers: { "X-CSRFTOKEN": null },
        },
      );
    });

    it("calls setErrors if the payment API fails", async () => {
      helper.handleRequestStub.withArgs(paymentAPI.toString()).returns({
        status: 400,
        body: ["Invalid application state"],
      });
      const setErrorsStub = helper.sandbox.stub();
      const setSubmittingStub = helper.sandbox.stub();
      const { formik } = await renderFormik();
      await formik.prop("onSubmit")(
        { amount: 1 },
        { setErrors: setErrorsStub, setSubmitting: setSubmittingStub },
      );
      sinon.assert.calledWith(setSubmittingStub, false);
      sinon.assert.calledWith(setErrorsStub, {
        amount: sinon.match.any,
      });
    });
  });
});
