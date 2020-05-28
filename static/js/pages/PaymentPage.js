// @flow
/* global SETTINGS: false */
import React from "react"
import { connect } from "react-redux"
import _ from "lodash"
import * as R from "ramda"
import URI from "urijs"
import moment from "moment"
import { mutateAsync, requestAsync } from "redux-query"

import {
  clearUI,
  hideDialog,
  setPaymentAmount,
  setSelectedBootcampRunKey,
  setTimeoutActive,
  setToastMessage,
  showDialog
} from "../actions"
import { TOAST_SUCCESS, TOAST_FAILURE } from "../constants"
import queries from "../lib/queries"
import { currentUserSelector } from "../lib/queries/users"
import { createForm, getRunWithFulfilledOrder } from "../util/util"
import Payment from "../components/Payment"
import PaymentHistory from "../components/PaymentHistory"
import Toast from "../components/Toast"

import type { UIState } from "../reducers/ui"
import type { InputEvent } from "../flow/events"
import type { PaymentPayload, PaymentResponse } from "../flow/ecommerceTypes"
import type { BootcampRun, BootcampRunsResponse } from "../flow/bootcampTypes"
import type { CurrentUser } from "../flow/authTypes"

type Props = {
  ui: UIState,
  clearUI: () => void,
  fetchBootcampRuns: (
    runKey: string
  ) => Promise<{ body: BootcampRunsResponse }>,
  hideDialog: (dialogKey: string) => void,
  sendPayment: (payload: PaymentPayload) => Promise<{ body: PaymentResponse }>,
  bootcampRuns: BootcampRunsResponse,
  bootcampRunsFinished: boolean,
  bootcampRunsProcessing: boolean,
  paymentProcessing: boolean,
  payableBootcampRunsData: BootcampRunsResponse,
  selectedBootcampRun: ?BootcampRun,
  setPaymentAmount: (amount: string) => void,
  setSelectedBootcampRunKey: (runKey: number) => void,
  setTimeoutActive: (active: boolean) => void,
  setToastMessage: (payload: any) => void,
  showDialog: (dialogKey: string) => void,
  currentUser: ?CurrentUser
}

export class PaymentPage extends React.Component<Props> {
  fetchAPIdata() {
    this.fetchBootcampRuns()
  }

  componentDidMount() {
    this.fetchAPIdata()
    this.handleOrderStatus()
  }

  componentDidUpdate(prevProps: Props) {
    // This is meant to be an identity check, not a deep equality check. This shows whether we received an update
    // for enrollments based on the forceReload
    if (prevProps.bootcampRuns !== this.props.bootcampRuns) {
      this.handleOrderStatus()
    }
  }

  componentWillUnmount() {
    const { clearUI } = this.props
    clearUI()
  }

  fetchBootcampRuns() {
    const {
      fetchBootcampRuns,
      bootcampRunsProcessing,
      currentUser
    } = this.props
    if (!bootcampRunsProcessing && currentUser) {
      // $FlowFixMe: an anon user shouldn't end up here
      fetchBootcampRuns(currentUser.username)
    }
  }

  sendPayment = async () => {
    const {
      sendPayment,
      ui: { paymentAmount },
      selectedBootcampRun
    } = this.props
    if (selectedBootcampRun && paymentAmount) {
      const result = await sendPayment({
        payment_amount: paymentAmount,
        run_key:        selectedBootcampRun.run_key
      })
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
  }

  setPaymentAmount = (event: InputEvent) => {
    const { setPaymentAmount } = this.props
    setPaymentAmount(event.target.value)
  }

  setSelectedBootcampRunKey = (event: InputEvent) => {
    const { setSelectedBootcampRunKey } = this.props
    setSelectedBootcampRunKey(parseInt(event.target.value))
  }

  getRunDataWithPayments = R.filter(
    R.compose(R.not, R.equals(0), R.propOr(0, "total_paid"))
  )

  handleOrderStatus = (): void => {
    const { bootcampRuns, bootcampRunsFinished } = this.props
    let query = new URI().query(true)
    if (!bootcampRunsFinished) {
      // wait until we have access to the bootcamp runs
      return
    }

    // hacky workaround to handle redirect from Cybersource while keeping query parameters
    if (query.next) {
      query = new URI(query.next).query(true)
    }

    const status = query.status
    if (status === "receipt") {
      const orderId = parseInt(query.order)
      const bootcampRun = getRunWithFulfilledOrder(bootcampRuns, orderId)
      if (bootcampRun) {
        this.handleOrderSuccess()
      } else {
        this.handleOrderPending()
      }
    } else if (status === "cancel") {
      this.handleOrderCancellation()
    }
  }

  handleOrderSuccess = (): void => {
    const {
      setToastMessage,
      ui: { toastMessage }
    } = this.props
    if (toastMessage === null) {
      setToastMessage({
        title: "Payment Complete!",
        icon:  TOAST_SUCCESS
      })
    }
    window.history.pushState({}, null, new URI().query({}).toString())
  }

  handleOrderPending = (): void => {
    const {
      fetchBootcampRuns,
      setTimeoutActive,
      setToastMessage,
      currentUser
    } = this.props
    if (!this.props.ui.timeoutActive) {
      setTimeout(() => {
        const { ui } = this.props
        setTimeoutActive(false)
        const deadline = moment(ui.initialTime).add(2, "minutes")
        const now = moment()
        // $FlowFixMe: an anon user won't end up here
        if (now.isBefore(deadline) && currentUser.username) {
          fetchBootcampRuns(currentUser.username)
        } else {
          setToastMessage({
            message: "Order was not processed",
            icon:    TOAST_FAILURE
          })
        }
      }, 3000)
      setTimeoutActive(true)
    }
  }

  handleOrderCancellation = (): void => {
    const {
      setToastMessage,
      ui: { toastMessage }
    } = this.props

    if (toastMessage === null) {
      setToastMessage({
        message: "Order was cancelled",
        icon:    TOAST_FAILURE
      })
    }
    window.history.pushState({}, null, new URI().query({}).toString())
  }

  clearMessage = (): void => {
    const { setToastMessage } = this.props
    setToastMessage(null)
  }

  renderToast() {
    const {
      ui: { toastMessage }
    } = this.props
    if (!toastMessage) {
      return null
    }

    const {
      icon: iconName,
      title: titleText,
      message: messageText
    } = toastMessage

    let icon, title, message
    if (iconName) {
      icon = (
        <i className="material-icons" key="icon">
          {iconName}
        </i>
      )
    }

    if (titleText) {
      title = <h1>{titleText}</h1>
    }
    if (messageText) {
      message = <p>{messageText}</p>
    }

    return (
      <Toast onTimeout={this.clearMessage}>
        <div className="toast-message">
          {icon}
          <div className="toast-body">
            {title}
            {message}
          </div>
        </div>
      </Toast>
    )
  }

  render() {
    const {
      hideDialog,
      ui,
      paymentProcessing,
      bootcampRuns,
      bootcampRunsFinished,
      payableBootcampRunsData,
      selectedBootcampRun,
      showDialog,
      currentUser
    } = this.props

    let renderedPayment = null
    let renderedPaymentHistory = null

    if (bootcampRunsFinished && currentUser) {
      renderedPayment = (
        <Payment
          hideDialog={hideDialog}
          showDialog={showDialog}
          ui={ui}
          paymentProcessing={paymentProcessing}
          payableBootcampRunsData={payableBootcampRunsData}
          selectedBootcampRun={selectedBootcampRun}
          now={moment()}
          sendPayment={this.sendPayment}
          setPaymentAmount={this.setPaymentAmount}
          setSelectedBootcampRunKey={this.setSelectedBootcampRunKey}
          currentUser={currentUser}
        />
      )

      const runDataWithPayments = this.getRunDataWithPayments(
        bootcampRuns || []
      )
      renderedPaymentHistory =
        runDataWithPayments.length > 0 ? (
          <div className="body-row">
            <PaymentHistory runDataWithPayments={runDataWithPayments} />
          </div>
        ) : null
    }

    return (
      <div>
        <div className="body-row top-content-container">
          {this.renderToast()}
          {renderedPayment}
        </div>
        {renderedPaymentHistory}
      </div>
    )
  }
}

const withPayableBootcampRuns = state => ({
  ...state,
  payableBootcampRunsData: state.bootcampRuns || []
})

const withDerivedSelectedRun = state => {
  const {
    payableBootcampRunsData,
    ui: { selectedBootcampRunKey }
  } = state

  let selectedBootcampRun
  if (_.isNumber(selectedBootcampRunKey)) {
    selectedBootcampRun = R.find(R.propEq("run_key", selectedBootcampRunKey))(
      payableBootcampRunsData
    )
  } else if (payableBootcampRunsData.length === 1) {
    selectedBootcampRun = payableBootcampRunsData[0]
  }

  return selectedBootcampRun ?
    { ...state, selectedBootcampRun: selectedBootcampRun } :
    state
}

const mapStateToProps = R.compose(
  withDerivedSelectedRun,
  withPayableBootcampRuns,
  state => ({
    paymentProcessing: R.pathOr(
      false,
      ["queries", "payment", "isPending"],
      state
    ),
    bootcampRuns:           R.pathOr([], ["entities", "bootcampRuns"], state),
    bootcampRunsProcessing: R.pathOr(
      false,
      ["queries", "bootcampRuns", "isPending"],
      state
    ),
    bootcampRunsFinished: R.pathOr(
      false,
      ["queries", "bootcampRuns", "isFinished"],
      state
    ),
    ui:          state.ui,
    currentUser: currentUserSelector(state)
  })
)

const mapDispatchToProps = dispatch => ({
  clearUI:           () => dispatch(clearUI()),
  fetchBootcampRuns: (username: string) =>
    dispatch(requestAsync(queries.bootcamps.bootcampRunQuery(username))),
  hideDialog:  (dialogKey: string) => dispatch(hideDialog(dialogKey)),
  sendPayment: (payload: PaymentPayload) =>
    dispatch(mutateAsync(queries.ecommerce.paymentMutation(payload))),
  setPaymentAmount:          (amount: string) => dispatch(setPaymentAmount(amount)),
  setSelectedBootcampRunKey: (runKey: number) =>
    dispatch(setSelectedBootcampRunKey(runKey)),
  setToastMessage:  (payload: any) => dispatch(setToastMessage(payload)),
  setTimeoutActive: (active: boolean) => dispatch(setTimeoutActive(active)),
  showDialog:       (dialogKey: string) => dispatch(showDialog(dialogKey))
})

export default connect(mapStateToProps, mapDispatchToProps)(PaymentPage)
