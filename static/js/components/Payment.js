// @flow
/* global SETTINGS: false */
import React from "react"
import * as R from "ramda"
import _ from "lodash"

import Dialog from "./Dialog"
import {
  isNilOrBlank,
  formatDollarAmount,
  formatReadableDate,
  getInstallmentDeadlineDates
} from "../util/util"
import type { UIState } from "../reducers/ui"
import type { InputEvent } from "../flow/events"

export const PAYMENT_CONFIRMATION_DIALOG = "paymentConfirmationDialog"
const isVisible = R.propOr(false, PAYMENT_CONFIRMATION_DIALOG)

export default class Payment extends React.Component<*, void> {
  props: {
    hideDialog: (dialogKey: string) => void,
    ui: UIState,
    paymentProcessing: boolean,
    payableBootcampRunsData: Array<Object>,
    selectedBootcampRun: Object,
    now: moment$Moment,
    sendPayment: () => void,
    setPaymentAmount: (event: InputEvent) => void,
    setSelectedBootcampRunKey: (event: InputEvent) => void,
    showDialog: (dialogKey: string) => void
  }

  getTotalOwedUpToInstallment = (nextInstallmentIndex: number): number => {
    const {
      selectedBootcampRun: { installments }
    } = this.props

    return R.compose(
      R.sum,
      R.map(R.prop("amount")),
      R.slice(0, nextInstallmentIndex + 1)
    )(installments)
  }

  hasMissedPreviousInstallment = (nextInstallmentIndex: number): boolean => {
    const { selectedBootcampRun } = this.props

    return (
      nextInstallmentIndex > 0 &&
      selectedBootcampRun.total_paid <
        this.getTotalOwedUpToInstallment(nextInstallmentIndex - 1)
    )
  }

  getPaymentDeadlineText = (): string => {
    const { selectedBootcampRun, now } = this.props

    const installments = selectedBootcampRun.installments
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
        if (selectedBootcampRun.total_paid < totalOwedForInstallment) {
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

  renderBootcampRunDropdown = () => {
    const {
      payableBootcampRunsData,
      ui: { selectedBootcampRunKey },
      setSelectedBootcampRunKey
    } = this.props

    const options = _.map(payableBootcampRunsData, bootcampRun => (
      <option value={bootcampRun.run_key} key={bootcampRun.run_key}>
        {bootcampRun.display_title}
      </option>
    ))
    options.unshift(
      <option value="" key="default" disabled style={{ display: "none" }}>
        Select...
      </option>
    )
    const valueProp = selectedBootcampRunKey ?
      { value: selectedBootcampRunKey } :
      { defaultValue: "" }

    return (
      <div className="klass-select-section">
        <p className="desc">Which Bootcamp do you want to pay for?</p>
        <div className="styled-select-container">
          <select
            className="klass-select"
            onChange={setSelectedBootcampRunKey}
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
      selectedBootcampRun,
      sendPayment,
      showDialog
    } = this.props
    const actualPrice = selectedBootcampRun.price

    paymentAmount > actualPrice ?
      showDialog(PAYMENT_CONFIRMATION_DIALOG) :
      sendPayment()
  }

  renderSelectedBootcampRun = () => {
    const {
      hideDialog,
      ui: { paymentAmount, dialogVisibility },
      paymentProcessing,
      selectedBootcampRun,
      setPaymentAmount,
      sendPayment
    } = this.props

    const totalPaid = selectedBootcampRun.total_paid || 0

    return (
      <div className="klass-display-section">
        <p className="desc">
          You have been accepted to {selectedBootcampRun.display_title}.<br />
          You have paid {formatDollarAmount(totalPaid)} out of{" "}
          {formatDollarAmount(selectedBootcampRun.price)}.
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
            disabled={paymentProcessing}
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
          onCancel={() => hideDialog(PAYMENT_CONFIRMATION_DIALOG)}
          onAccept={sendPayment}
          submitText="Continue"
          open={isVisible(dialogVisibility)}
          hideDialog={() => hideDialog(PAYMENT_CONFIRMATION_DIALOG)}
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
    const { payableBootcampRunsData, selectedBootcampRun } = this.props

    const welcomeMessage = !isNilOrBlank(SETTINGS.user.full_name) ? (
      <h1 className="greeting">Hi {SETTINGS.user.full_name}!</h1>
    ) : null
    let renderedRunChoice
    if (payableBootcampRunsData.length > 1) {
      renderedRunChoice = this.renderBootcampRunDropdown()
    } else if (payableBootcampRunsData.length === 0) {
      renderedRunChoice = (
        <p className="desc">No payment is required at this time.</p>
      )
    }
    const renderedSelectedRun = selectedBootcampRun ?
      this.renderSelectedBootcampRun() :
      null

    return (
      <div className="payment-section">
        {welcomeMessage}
        {renderedRunChoice}
        {renderedSelectedRun}
      </div>
    )
  }
}
