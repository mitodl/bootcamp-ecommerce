// @flow
import { assert } from "chai";
import sinon from "sinon";

import PaymentHistoryPage from "./PaymentHistoryPage";

import { calcOrderBalances } from "../../lib/applicationApi";
import IntegrationTestHelper from "../../util/integration_test_helper";
import { makeCountries } from "../../factories/user";
import { makeApplicationDetail } from "../../factories/application";
import {
  formatPrice,
  formatReadableDateFromStr,
  formatRunDateRange,
} from "../../util/util";
import { generateOrder, generateLegacyOrderPartial } from "../../factories";
import { isIf, shouldIf } from "../../lib/test_utils";

describe("PaymentHistoryPage", () => {
  let helper, countries, fakeApplicationDetail, renderPage;

  beforeEach(() => {
    countries = makeCountries();
    fakeApplicationDetail = makeApplicationDetail();

    helper = new IntegrationTestHelper();
    helper.handleRequestStub
      .withArgs(`/api/applications/${String(fakeApplicationDetail.id)}/`)
      .returns({
        status: 200,
        body: fakeApplicationDetail,
      });
    helper.handleRequestStub.withArgs("/api/countries/").returns({
      status: 200,
      body: countries,
    });

    renderPage = helper.configureReduxQueryRenderer(PaymentHistoryPage, {
      match: {
        params: { applicationId: fakeApplicationDetail.id },
      },
    });
    window.print = helper.sandbox.stub();
  });

  afterEach(() => {
    helper.cleanup();
  });

  it("prints", async () => {
    const { wrapper } = await renderPage();
    wrapper.find(".print").prop("onClick")();
    sinon.assert.calledWith(window.print);
  });

  it("shows the bootcamp title and dates", async () => {
    const { wrapper } = await renderPage();
    assert.include(
      wrapper.find(".bootcamp-title").text(),
      fakeApplicationDetail.bootcamp_run.title,
    );
    assert.include(
      wrapper.find(".bootcamp-dates").text(),
      formatRunDateRange(fakeApplicationDetail.bootcamp_run),
    );
  });

  it("renders order information", async () => {
    fakeApplicationDetail.orders.push(generateOrder());

    const { wrapper } = await renderPage();
    const { ordersAndBalances } = calcOrderBalances(fakeApplicationDetail);

    fakeApplicationDetail.orders.forEach((order, i) => {
      const orderWrapper = wrapper.find(".order").at(i);
      assert.include(
        orderWrapper.find(".payment-date").text(),
        "Payment Date:",
      );
      assert.include(
        orderWrapper.find(".payment-date").text(),
        formatReadableDateFromStr(order.updated_on),
      );
      assert.include(orderWrapper.find(".amount-paid").text(), "Amount Paid:");
      assert.include(
        orderWrapper.find(".amount-paid").text(),
        formatPrice(order.total_price_paid),
      );
      assert.include(
        orderWrapper.find(".balance").text(),
        formatPrice(ordersAndBalances[i].balance),
      );
      assert.include(
        orderWrapper.find(".payment-method").text(),
        order.payment_method,
      );
    });
  });

  it("renders refund information", async () => {
    const refund = {
      ...generateLegacyOrderPartial(),
      total_price_paid: -10,
      payment_method: "Visa:1234",
    };

    fakeApplicationDetail.orders = [refund];

    const { wrapper } = await renderPage();
    const { ordersAndBalances } = calcOrderBalances(fakeApplicationDetail);

    const orderWrapper = wrapper.find(".order");
    assert.include(orderWrapper.find(".payment-date").text(), "Refund Date:");
    assert.include(
      orderWrapper.find(".payment-date").text(),
      formatReadableDateFromStr(refund.updated_on),
    );
    assert.include(
      orderWrapper.find(".amount-paid").text(),
      "Amount Refunded:",
    );
    assert.include(
      orderWrapper.find(".amount-paid").text(),
      formatPrice(refund.total_price_paid),
    );
    assert.include(
      orderWrapper.find(".balance").text(),
      formatPrice(ordersAndBalances[0].balance),
    );
    assert.include(
      orderWrapper.find(".payment-method").text(),
      refund.payment_method,
    );
  });

  it("does not render the payment method if it is blank", async () => {
    const nullPaymentMethodOrder = {
      ...generateLegacyOrderPartial(),
      total_price_paid: 10,
      payment_method: "",
    };

    fakeApplicationDetail.orders = [nullPaymentMethodOrder];

    const { wrapper } = await renderPage();
    assert.isNotOk(wrapper.find(".payment-method").exists());
  });

  it("renders the summary", async () => {
    const { wrapper } = await renderPage();
    const { balanceRemaining, totalPaid, totalPrice } = calcOrderBalances(
      fakeApplicationDetail,
    );
    assert.include(
      wrapper.find(".summary .total-paid").text(),
      formatPrice(totalPaid),
    );
    assert.include(
      wrapper.find(".summary .balance").text(),
      formatPrice(balanceRemaining),
    );
    assert.include(
      wrapper.find(".summary .amount-due").text(),
      formatPrice(totalPrice),
    );
  });

  it("renders customer information", async () => {
    const { wrapper } = await renderPage();
    assert.include(
      wrapper.find(".name").text(),
      // $FlowFixMe
      fakeApplicationDetail.user.profile.name,
    );
    assert.include(
      wrapper.find(".email").text(),
      // $FlowFixMe
      fakeApplicationDetail.user.email,
    );
    assert.deepEqual(wrapper.find("Address").props(), {
      application: fakeApplicationDetail,
      countries,
    });
  });

  //
  [true, false].forEach((isLoading) => {
    it(`${shouldIf(isLoading)} show a loader if the page ${isIf(
      isLoading,
    )} loading`, async () => {
      helper.isLoadingStub.returns(isLoading);
      const { wrapper } = await renderPage();
      assert.equal(wrapper.find("FullLoader").exists(), isLoading);
    });
  });
});
