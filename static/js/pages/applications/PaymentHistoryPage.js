// @flow
import React from "react";
import { connect } from "react-redux";
import { compose, path, pathOr } from "ramda";
import { connectRequest } from "redux-query-react";

import Address from "../../components/Address";
import FullLoader from "../../components/loaders/FullLoader";

import { calcOrderBalances } from "../../lib/applicationApi";
import queries from "../../lib/queries";
import {
  formatPrice,
  formatReadableDateFromStr,
  formatRunDateRange,
} from "../../util/util";

import type { ApplicationDetail } from "../../flow/applicationTypes";
import type { Country } from "../../flow/authTypes";

type OwnProps = {
  match: {
    params: {
      applicationId: string,
    },
  },
};

type Props = OwnProps & {
  application: ?ApplicationDetail,
  countries: ?Array<Country>,
};
export function PaymentHistoryPage({ application, countries }: Props) {
  if (!application || !countries) {
    return <FullLoader />;
  }

  const { ordersAndBalances, totalPaid, totalPrice, balanceRemaining } =
    calcOrderBalances(application);

  const isRefund = (order: any) => {
    return order.total_price_paid < 0;
  };

  return (
    <div className="payment-history container">
      <div className="payment-history-header">
        <h1>Payment Statement</h1>
        <a className="print" onClick={() => window.print()}>
          <span className="material-icons">printer</span>
          <span>Print</span>
        </a>
      </div>
      <img src="/static/images/mit-bootcamps-logo.svg" alt="MIT Bootcamps" />
      <div className="payment-history-container">
        <div className="bootcamp-info inner-container">
          <h2 className="col-12">Order Information</h2>
          <div className="row bootcamp-title">
            <div className="key col-3">Bootcamp:</div>
            <div className="col-9">{application.bootcamp_run.title}</div>
          </div>
          <div className="row bootcamp-dates">
            <div className="key col-3">Dates:</div>
            <div className="col-9">
              {formatRunDateRange(application.bootcamp_run)}
            </div>
          </div>
        </div>
        <div className="order-container inner-container">
          {ordersAndBalances.map(({ order, balance }) => (
            <div key={order.id}>
              <h2 className="col-12">Order Information</h2>
              <div className="order">
                <div className="payment-date row">
                  <div className="col-3 key">
                    {isRefund(order) ? "Refund Date:" : "Payment Date:"}
                  </div>
                  <div className="col-9">
                    {formatReadableDateFromStr(order.updated_on)}
                  </div>
                </div>
                <div className="amount-paid row">
                  <div className="col-3 key">
                    {isRefund(order) ? "Amount Refunded:" : "Amount Paid:"}
                  </div>
                  <div className="col-9">
                    {formatPrice(order.total_price_paid)}
                  </div>
                </div>
                <div className="balance row">
                  <div className="col-3 key">Balance:</div>
                  <div className="col-9">{formatPrice(balance)}</div>
                </div>
                {order.payment_method ? (
                  <div className="payment-method row">
                    <div className="col-3 key">Payment Method:</div>
                    <div className="col-9">{order.payment_method}</div>
                  </div>
                ) : null}
              </div>
              <hr />
            </div>
          ))}
          <div className="summary">
            <div className="row total-paid">
              <div className="col-3 summary-key">Total Amount Paid:</div>
              <div className="col-9">{formatPrice(totalPaid)}</div>
            </div>
            <div className="row balance">
              <div className="col-3 summary-key">Balance Due:</div>
              <div className="col-9">{formatPrice(balanceRemaining)}</div>
            </div>
            <div className="row amount-due">
              <div className="col-3 summary-key">Total Amount Due:</div>
              <div className="col-9">{formatPrice(totalPrice)}</div>
            </div>
          </div>
        </div>
        <div className="customer inner-container">
          <h2 className="col-12">Customer Information</h2>
          <div className="row name">
            <div className="col-3 key">Name:</div>
            <div className="col-9">
              {pathOr("", ["user", "profile", "name"], application)}
            </div>
          </div>
          <div className="row email">
            <div className="col-3 key">Email address:</div>
            <div className="col-9">{application.user.email}</div>
          </div>
          <div className="row address">
            <div className="col-3 key">Address:</div>
            <div className="col-9">
              <Address application={application} countries={countries} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const mapStateToProps = (state, ownProps: OwnProps) => {
  const applicationId = ownProps.match.params.applicationId;
  const application = path(
    ["entities", "applicationDetail", applicationId],
    state,
  );

  return {
    application,
    countries: queries.users.countriesSelector(state),
  };
};
const mapPropsToConfigs = (props: Props) => [
  queries.applications.applicationDetailQuery(props.match.params.applicationId),
  queries.users.countriesQuery(),
];
export default compose(
  connect(mapStateToProps),
  connectRequest(mapPropsToConfigs),
)(PaymentHistoryPage);
