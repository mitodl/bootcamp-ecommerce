// @flow
/* global SETTINGS: false */
import React from "react"
import * as R from "ramda"

import { formatDollarAmount } from "../util/util"

export default class PaymentHistory extends React.Component<*, void> {
  props: {
    runDataWithPayments: Array<Object>
  }

  renderPaymentRow = (bootcampRun: Object) => {
    const paymentAmountMsg =
      bootcampRun.total_paid !== bootcampRun.price ?
        `${formatDollarAmount(
          bootcampRun.total_paid
        )} out of ${formatDollarAmount(bootcampRun.price)}` :
        `${formatDollarAmount(bootcampRun.total_paid)}`

    return (
      <tr key={bootcampRun.run_key}>
        <td>{bootcampRun.display_title}</td>
        <td>{paymentAmountMsg}</td>
        <td className="statement-column">
          <i className="material-icons">print</i>
          <a
            href={`/statement/${bootcampRun.run_key}`}
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
    const { runDataWithPayments } = this.props

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
            <tbody>{R.map(this.renderPaymentRow, runDataWithPayments)}</tbody>
          </table>
        </div>
      </div>
    )
  }
}
