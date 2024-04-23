import React from "react";
import { shallow } from "enzyme";
import { assert } from "chai";
import _ from "lodash";

import PaymentHistory from "./PaymentHistory";
import { generateFakePayableRuns } from "../factories";

describe("PaymentHistory", () => {
  const statementLinkSelector = "a.statement-link";

  const renderPaymentHistory = (runDataWithPayments) =>
    shallow(<PaymentHistory runDataWithPayments={runDataWithPayments} />);

  const setPaymentValues = (bootcampRunsData, paymentAmount) =>
    _.map(bootcampRunsData, (bootcampRun) =>
      _.set(bootcampRun, "total_paid", paymentAmount),
    );

  it("should show rows of payment history information", () => {
    const bootcampCount = 3;
    const paymentAmount = 100;
    let fakeRuns = generateFakePayableRuns(bootcampCount);
    // Set all fake bootcamp runs to have payments
    fakeRuns = setPaymentValues(fakeRuns, paymentAmount);
    fakeRuns[0].price = 1000;
    fakeRuns[1].price = paymentAmount;

    const wrapper = renderPaymentHistory(fakeRuns);
    const paymentHistoryTableRows = wrapper.find("tbody tr");
    assert.equal(paymentHistoryTableRows.length, bootcampCount);
    const firstRowHtml = paymentHistoryTableRows.at(0).html();
    assert.include(firstRowHtml, fakeRuns[0].display_title);
    assert.include(firstRowHtml, `$${paymentAmount} out of $1,000`);
    const secondRowHtml = paymentHistoryTableRows.at(1).html();
    assert.include(secondRowHtml, fakeRuns[1].display_title);
    assert.include(secondRowHtml, `$${paymentAmount}`);
  });

  it("should show a link to view a payment statement", () => {
    const fakeRuns = generateFakePayableRuns(1);
    const wrapper = renderPaymentHistory(fakeRuns);
    const statementLink = wrapper.find(statementLinkSelector);
    assert.equal(
      statementLink.prop("href"),
      `/statement/${fakeRuns[0].run_key}`,
    );
  });
});
