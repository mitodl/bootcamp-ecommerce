// @flow
/* global SETTINGS: false */
import React from "react"
import * as R from "ramda"
import _ from "lodash"
import type { Dispatch } from "redux"

import Dialog from "./Dialog"
import { showDialog, hideDialog } from "../actions/index"
import {
  isNilOrBlank,
  formatDollarAmount,
  formatReadableDate,
  getInstallmentDeadlineDates
} from "../util/util"
import type { UIState } from "../reducers"
import type { RestState } from "../rest"
import type { InputEvent } from "../flow/events"

export const PAYMENT_CONFIRMATION_DIALOG = "paymentConfirmationDialog"
const isVisible = R.propOr(false, PAYMENT_CONFIRMATION_DIALOG)

export default class Payment extends React.Component<*, void> {
  props: {
    dispatch: Dispatch<*>,
    ui: UIState,
    payment: RestState,
    payableKlassesData: Array<Object>,
    selectedKlass: Object,
    now: moment$Moment,
    sendPayment: () => void,
    setPaymentAmount: (event: InputEvent) => void,
    setSelectedKlassKey: (event: InputEvent) => void
  }

  getTotalOwedUpToInstallment = (nextInstallmentIndex: number): number => {
    const {
      selectedKlass: { installments }
    } = this.props

    return R.compose(
      R.sum,
      R.map(R.prop("amount")),
      R.slice(0, nextInstallmentIndex + 1)
    )(installments)
  }

  hasMissedPreviousInstallment = (nextInstallmentIndex: number): boolean => {
    const { selectedKlass } = this.props

    return (
      nextInstallmentIndex > 0 &&
      selectedKlass.total_paid <
        this.getTotalOwedUpToInstallment(nextInstallmentIndex - 1)
    )
  }

  getPaymentDeadlineText = (): string => {
    const { selectedKlass, now } = this.props

    const installments = selectedKlass.installments
    let installmentDeadlineText = ""

    if (installments.length > 0) {
      const deadlineDates = getInstallmentDeadlineDates(installments)
      const finalInstallmentDeadline = formatReadableDate(R.last(deadlineDates))
      const nextInstallmentIndex = R.findIndex(R.lt(now), deadlineDates)
      const lastInstallmentIndex = installments.length - 1
      if (nextInstallmentIndex !== lastInstallmentIndex) {
        const totalOwedForInstallment = this.getTotalOwedUpToInstallment(
          nextInstallmentIndex
        )
        if (selectedKlass.total_paid < totalOwedForInstallment) {
          installmentDeadlineText =
            `A deposit of ${formatDollarAmount(totalOwedForInstallment)} ` +
            `is due ${formatReadableDate(deadlineDates[nextInstallmentIndex])}.`
        }
      }
      if (this.hasMissedPreviousInstallment(nextInstallmentIndex)) {
        installmentDeadlineText = `You missed the previous payment deadline. ${installmentDeadlineText}`
      }
      installmentDeadlineText += ` Full payment must be complete by ${finalInstallmentDeadline}.`
    }

    return installmentDeadlineText
  }

  renderKlassDropdown = () => {
    const {
      payableKlassesData,
      ui: { selectedKlassKey },
      setSelectedKlassKey
    } = this.props

    const options = _.map(payableKlassesData, klass => (
      <option value={klass.klass_key} key={klass.klass_key}>
        {klass.display_title}
      </option>
    ))
    options.unshift(
      <option value="" key="default" disabled style={{ display: "none" }}>
        Select...
      </option>
    )
    const valueProp = selectedKlassKey ?
      { value: selectedKlassKey } :
      { defaultValue: "" }

    return (
      <div className="klass-select-section">
        <p className="desc">Which Bootcamp do you want to pay for?</p>
        <div className="styled-select-container">
          <select
            className="klass-select"
            onChange={setSelectedKlassKey}
            {...valueProp}
          >
            {options}
          </select>
        </div>
      </div>
    )
  }

  confirmPayment = () => {
    const {
      ui: { paymentAmount },
      selectedKlass,
      sendPayment,
      dispatch
    } = this.props
    const actualPrice = selectedKlass.price

    paymentAmount > actualPrice ?
      dispatch(showDialog(PAYMENT_CONFIRMATION_DIALOG)) :
      sendPayment()
  }

  renderSelectedKlass = () => {
    const {
      ui: { paymentAmount, dialogVisibility },
      payment: { processing },
      selectedKlass,
      setPaymentAmount,
      sendPayment,
      dispatch
    } = this.props

    const totalPaid = selectedKlass.total_paid || 0

    return (
      <div className="klass-display-section">
        <p className="desc">
          You have been accepted to {selectedKlass.display_title}.<br />
          You have paid {formatDollarAmount(totalPaid)} out of{" "}
          {formatDollarAmount(selectedKlass.price)}.
        </p>
        <p className="deadline-message">{this.getPaymentDeadlineText()}</p>
        <div className="payment">
          <input
            type="number"
            id="payment-amount"
            value={paymentAmount}
            onChange={setPaymentAmount}
            placeholder="Enter amount"
          />
          <button
            className="btn large-cta"
            onClick={this.confirmPayment}
            disabled={processing}
          >
            Pay Now
          </button>
          <br />
          <p className="tac">
            By making a payment I certify that I agree with the{" "}
            <a
              href="/terms_and_conditions/"
              target="_blank"
              className="tac-link"
            >
              MIT Bootcamps Terms and Conditions
            </a>
          </p>
        </div>
        <Dialog
          title="Confirm Payment"
          onCancel={() => dispatch(hideDialog(PAYMENT_CONFIRMATION_DIALOG))}
          onAccept={sendPayment}
          submitText="Continue"
          open={isVisible(dialogVisibility)}
          hideDialog={() => dispatch(hideDialog(PAYMENT_CONFIRMATION_DIALOG))}
        >
          <p className="overpay-confirm">
            Are you sure you want to pay{" "}
            {formatDollarAmount(parseFloat(paymentAmount))}?
          </p>
        </Dialog>
      </div>
    )
  }

  render() {
    const { payableKlassesData, selectedKlass } = this.props

    const welcomeMessage = !isNilOrBlank(SETTINGS.user.full_name) ? (
      <h1 className="greeting">Hi {SETTINGS.user.full_name}!</h1>
    ) : null
    let renderedKlassChoice
    if (payableKlassesData.length > 1) {
      renderedKlassChoice = this.renderKlassDropdown()
    } else if (payableKlassesData.length === 0) {
      renderedKlassChoice = (
        <p className="desc">No payment is required at this time.</p>
      )
    }
    const renderedSelectedKlass = selectedKlass ?
      this.renderSelectedKlass() :
      null

    return (
      <div className="payment-section">
        {welcomeMessage}
        {renderedKlassChoice}
        {renderedSelectedKlass}
      </div>
    )
  }
}
