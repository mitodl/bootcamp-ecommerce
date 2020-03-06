// @flow
/* global SETTINGS: false */
import React from "react"
import R from "ramda"

import { formatDollarAmount } from "../util/util"

export default class PaymentHistory extends React.Component<*, void> {
  props: {
    klassDataWithPayments: Array<Object>
  }

  renderPaymentRow = (klass: Object) => {
    const paymentAmountMsg =
      klass.total_paid !== klass.price
        ? `${formatDollarAmount(klass.total_paid)} out of ${formatDollarAmount(
          klass.price
        )}`
        : `${formatDollarAmount(klass.total_paid)}`

    return (
      <tr key={klass.klass_key}>
        <td>{klass.display_title}</td>
        <td>{paymentAmountMsg}</td>
        <td className="statement-column">
          <i className="material-icons">print</i>
          <a
            href={`/statement/${klass.klass_key}`}
            target="_blank"
            rel="noopener noreferrer"
            className="statement-link"
          >
            View Statement
          </a>
        </td>
      </tr>
    )
  }

  render() {
    const { klassDataWithPayments } = this.props

    return (
      <div className="payment-history-section">
        <div className="payment-history-block">
          <h3 className="section-header">
            Payment History
            <hr />
          </h3>
          <table>
            <thead>
              <tr>
                <th className="col1">Bootcamp</th>
                <th className="col2">Amount Paid</th>
                <th className="col3" />
              </tr>
            </thead>
            <tbody>{R.map(this.renderPaymentRow, klassDataWithPayments)}</tbody>
          </table>
        </div>
      </div>
    )
  }
}
