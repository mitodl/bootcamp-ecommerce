// @flow
/* global SETTINGS: false */
import React from 'react';
import R from 'ramda';

import { formatDollarAmount } from '../util/util';
import type { RestState } from '../rest';

export default class PaymentHistory extends React.Component {
  props: {
    klasses: RestState
  };

  renderPaymentRow = (klass: Object) => {
    let paymentAmountMsg = klass.total_paid !== klass.price ?
      `${formatDollarAmount(klass.total_paid)} out of ${formatDollarAmount(klass.price)}` :
      `${formatDollarAmount(klass.total_paid)}`;

    return <tr key={klass.klass_key}>
      <td>{klass.klass_name}</td>
      <td>{paymentAmountMsg}</td>
      <td className="statement-column">
        <i className="material-icons">print</i><a href="#" className="statement-link">View Statement</a>
      </td>
    </tr>;
  };

  renderPaymentRows = R.pipe(
    R.filter(
      R.compose(
        R.not,
        R.equals(0),
        R.propOr(0, 'total_paid')
      )
    ),
    R.map(this.renderPaymentRow)
  );

  render() {
    const { klasses } = this.props;

    return <div className="payment-history-section">
      <div className="payment-history-block">
        <h3>Payment History</h3>
        <table>
          <thead>
            <tr>
              <th className="col1">Bootcamp</th>
              <th className="col2">Amount Paid</th>
              <th className="col3" />
            </tr>
          </thead>
          <tbody>
            {this.renderPaymentRows(klasses.data)}
          </tbody>
        </table>
      </div>
    </div>;
  }
}
