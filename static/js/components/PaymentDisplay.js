// @flow
import React, { useState } from "react"
import { path, sum } from "ramda"

import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"
import queries from "../lib/queries"
import { parsePrice } from "../util/util"

import {
  createForm,
  formatPrice,
  formatReadableDateFromStr
} from "../util/util"

import type { PaymentPayload } from "../flow/ecommerceTypes"
import type { ApplicationDetail } from "../flow/applicationTypes"

type Props = {
  application: ?ApplicationDetail,
  sendPayment: (payload: PaymentPayload) => Promise<void>
}

export function PaymentDisplay(props: Props) {
  const [amount, setAmount] = useState(0)
  const { application, sendPayment } = props
  if (!application) {
    return null
  }

  const run = application.bootcamp_run
  const totalSpent = sum(
    application.orders.map(order => order.total_price_paid)
  )
  const installments = run.installments
  const cost = sum(installments.map(installment => installment.amount))

  return (
    <div className="container">
      <div className="payment-drawer auth-card">
        <h2 className="drawer-title">Make Payment</h2>
        <div className="bootcamp">
          <div className="bootcamp-title">{run.bootcamp.title}</div>
          <div className="bootcamp-dates">
            {run.start_date ? formatReadableDateFromStr(run.start_date) : "TBD"}{" "}
            - {run.end_date ? formatReadableDateFromStr(run.end_date) : "TBD"}
          </div>
        </div>
        <div className="payment-deadline">
          Full payment must be complete by{" "}
          {formatReadableDateFromStr(application.payment_deadline)}
        </div>
        <div className="payment-amount">
          You have paid {formatPrice(totalSpent)} out of {formatPrice(cost)}.
        </div>
        <div className="payment-input-container">
          <input
            type="text"
            placeholder="Enter Amount"
            onChange={e => setAmount(e.target.value)}
          />
          <button
            className="btn btn-danger"
            onClick={() => {
              const price = parsePrice(amount)
              if (price === null || !price.toNumber()) {
                return
              }

              return sendPayment({
                application_id: application.id,
                payment_amount: price.toString()
              })
            }}
          >
            Pay Now
          </button>
        </div>
        <div className="terms-and-conditions">
          By making a payment I certify that I agree with the MIT Bootcamps{" "}
          <a href="/terms_and_conditions/" target="_blank">
            Terms and Conditions
          </a>
          .
        </div>
      </div>
    </div>
  )
}

const mapStateToProps = state => {
  const applicationId = path(["drawer", "drawerMeta", "applicationId"], state)
  const application = path(
    ["entities", "applicationDetail", applicationId],
    state
  )

  return {
    application
  }
}
const mapDispatchToProps = dispatch => ({
  sendPayment: async (paymentPayload: PaymentPayload) => {
    const result = await dispatch(
      mutateAsync(queries.ecommerce.paymentMutation(paymentPayload))
    )
    const {
      body: { url, payload }
    } = result
    const form = createForm(url, payload)
    const body = document.querySelector("body")
    if (!body) {
      // for flow
      throw new Error("No body in document")
    }
    body.appendChild(form)
    form.submit()
  }
})

export default compose(connect(mapStateToProps, mapDispatchToProps))(
  PaymentDisplay
)
