// @flow
/* global SETTINGS: false */
import React from "react"
import { sum } from "ramda"

import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"
import { ErrorMessage, Field, Form, Formik } from "formik"
import Decimal from "decimal.js-light"

import FormError from "./forms/elements/FormError"
import { closeDrawer } from "../reducers/drawer"
import queries from "../lib/queries"
import ButtonWithLoader from "./loaders/ButtonWithLoader"
import SupportLink from "./SupportLink"
import {
  formatRunDateRange,
  createForm,
  formatPrice,
  formatReadableDateFromStr,
  isNilOrBlank
} from "../util/util"

import type { PaymentPayload } from "../flow/ecommerceTypes"
import type { ApplicationDetail } from "../flow/applicationTypes"

type Props = {
  application: ?ApplicationDetail,
  sendPayment: (payload: PaymentPayload) => Promise<void>,
  closeDrawer: () => void
}

const roundToCent = amount => new Decimal(amount).toDecimalPlaces(2).toNumber()

const validate = ({ amount, balance }) => {
  let adjustedAmount
  if (isNilOrBlank(amount)) {
    return {
      amount: "Payment amount is required"
    }
  }
  try {
    adjustedAmount = roundToCent(amount)
  } catch (e) {
    return {
      amount: "Payment amount must be a valid number"
    }
  }
  if (adjustedAmount > balance) {
    return {
      amount: "Payment amount must be less than the remaining balance"
    }
  } else if (adjustedAmount <= 0) {
    return {
      amount: "Payment amount must be greater than zero"
    }
  }

  return {}
}

export const PaymentDisplay = (props: Props) => {
  const { application, sendPayment, closeDrawer } = props
  if (!application) {
    return null
  }

  const run = application.bootcamp_run
  const totalSpent = sum(
    application.orders.map(order => order.total_price_paid)
  )
  const cost = application.price

  return (
    <div className="container drawer-wrapper payment-drawer">
      <h2>Make Payment</h2>
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
          onSubmit={async (values, actions) => {
            const amount = values.amount
            try {
              await sendPayment({
                application_id: application.id,
                payment_amount: roundToCent(amount)
              })
              actions.resetForm()
              closeDrawer()
            } catch {
              actions.setErrors({
                amount: (
                  <span>
                    Something went wrong while submitting your payment. Please
                    try again, or <SupportLink />
                  </span>
                )
              })
              actions.setSubmitting(false)
            }
          }}
          render={({ isSubmitting, isValidating }) => (
            <Form>
              <Field type="number" name="amount" placeholder="Enter Amount" />
              <ButtonWithLoader
                className="btn-danger"
                type="submit"
                loading={isValidating || isSubmitting}
              >
                Pay Now
              </ButtonWithLoader>
              <ErrorMessage name="amount" component={FormError} />
            </Form>
          )}
        />
      </div>
      <div className="terms-and-conditions">
        By making a payment I certify that I agree with the MIT Bootcamps{" "}
        <a href={SETTINGS.terms_url}>Terms and Conditions</a>.
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
    if (!url || !payload) {
      throw new Error(result.body)
    }
    const form = createForm(url, payload)
    const body = document.querySelector("body")
    if (!body) {
      // for flow
      throw new Error("No body in document")
    }
    body.appendChild(form)
    form.submit()
  },
  closeDrawer: () => dispatch(closeDrawer())
})

export default compose(connect(null, mapDispatchToProps))(PaymentDisplay)
