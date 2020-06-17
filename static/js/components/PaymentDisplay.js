// @flow
import React from "react"
import { sum } from "ramda"

import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"
import { ErrorMessage, Field, Form, Formik } from "formik"
import Decimal from "decimal.js-light"

import queries from "../lib/queries"
import { formatRunDateRange } from "../util/util"

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

const roundToCent = amount => new Decimal(amount).toDecimalPlaces(2).toNumber()

const validate = ({ amount, balance }) => {
  if (roundToCent(amount) > balance) {
    return {
      amount: "Enter a number less than the remaining balance"
    }
  }

  return {}
}

const validateAmount = value => {
  let price
  try {
    price = roundToCent(value)
  } catch (e) {
    return "Price must be a valid number"
  }

  if (price <= 0) {
    return "Price must be greater than zero"
  }

  return null
}

export const PaymentDisplay = (props: Props) => {
  const { application, sendPayment } = props
  if (!application) {
    return null
  }

  const run = application.bootcamp_run
  const totalSpent = sum(
    application.orders.map(order => order.total_price_paid)
  )
  const cost = application.price

  return (
    <div className="container p-0">
      <div className="payment-drawer">
        <h2 className="drawer-title">Make Payment</h2>
        <div className="bootcamp">
          <div className="bootcamp-title">{run.bootcamp.title}</div>
          <div className="bootcamp-dates">{formatRunDateRange(run)}</div>
        </div>
        <div className="payment-deadline">
          Full payment must be complete by{" "}
          {formatReadableDateFromStr(application.payment_deadline)}
        </div>
        <div className="payment-amount">
          You have paid {formatPrice(totalSpent)} out of {formatPrice(cost)}.
        </div>
        <div className="payment-input-container">
          <Formik
            initialValues={{ amount: "", balance: cost }}
            validate={validate}
            onSubmit={async ({ amount }, actions) => {
              await sendPayment({
                application_id: application.id,
                payment_amount: roundToCent(amount)
              })
              actions.setSubmitting(false)
            }}
            render={({ isSubmitting }) => (
              <Form>
                <ErrorMessage name="amount" />
                <Field
                  name="amount"
                  type="text"
                  placeholder="Enter Amount"
                  validate={validateAmount}
                />
                <button
                  className="btn btn-danger"
                  type="submit"
                  disabled={isSubmitting}
                >
                  Pay Now
                </button>
              </Form>
            )}
          />
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

export default compose(connect(null, mapDispatchToProps))(PaymentDisplay)
