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
  setSelectedKlassKey,
  setTimeoutActive,
  setToastMessage,
  showDialog
} from "../actions"
import { TOAST_SUCCESS, TOAST_FAILURE } from "../constants"
import queries from "../lib/queries"
import { createForm, getKlassWithFulfilledOrder } from "../util/util"
import Payment from "../components/Payment"
import PaymentHistory from "../components/PaymentHistory"
import Toast from "../components/Toast"

import type { UIState } from "../reducers/ui"
import type { InputEvent } from "../flow/events"
import type { PaymentPayload, PaymentResponse } from "../flow/ecommerceTypes"
import type { Klass, KlassesResponse } from "../flow/klassTypes"

type Props = {
  ui: UIState,
  clearUI: () => void,
  fetchKlasses: (klassKey: string) => Promise<{ body: KlassesResponse }>,
  hideDialog: (dialogKey: string) => void,
  sendPayment: (payload: PaymentPayload) => Promise<{ body: PaymentResponse }>,
  klasses: KlassesResponse,
  klassesFinished: boolean,
  klassesProcessing: boolean,
  paymentProcessing: boolean,
  payableKlassesData: KlassesResponse,
  selectedKlass: ?Klass,
  setPaymentAmount: (amount: string) => void,
  setSelectedKlassKey: (klassKey: number) => void,
  setTimeoutActive: (active: boolean) => void,
  setToastMessage: (payload: any) => void,
  showDialog: (dialogKey: string) => void
}

export class PaymentPage extends React.Component<Props> {
  fetchAPIdata() {
    this.fetchKlasses()
  }

  componentDidMount() {
    this.fetchAPIdata()
    this.handleOrderStatus()
  }

  componentWillUnmount() {
    const { clearUI } = this.props
    clearUI()
  }

  fetchKlasses() {
    const { fetchKlasses, klassesProcessing } = this.props
    if (!klassesProcessing) {
      fetchKlasses(SETTINGS.user.username)
    }
  }

  sendPayment = async () => {
    const {
      sendPayment,
      ui: { paymentAmount },
      selectedKlass
    } = this.props
    if (selectedKlass && paymentAmount) {
      const result = await sendPayment({
        payment_amount: paymentAmount,
        klass_key:      selectedKlass.klass_key
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

  setSelectedKlassKey = (event: InputEvent) => {
    const { setSelectedKlassKey } = this.props
    setSelectedKlassKey(parseInt(event.target.value))
  }

  getKlassDataWithPayments = R.filter(
    R.compose(R.not, R.equals(0), R.propOr(0, "total_paid"))
  )

  handleOrderStatus = (): void => {
    const { klasses, klassesFinished } = this.props
    const query = new URI().query(true)
    if (!klassesFinished) {
      // wait until we have access to the klasses
      return
    }

    const status = query.status
    if (status === "receipt") {
      const orderId = parseInt(query.order)
      const klass = getKlassWithFulfilledOrder(klasses, orderId)
      if (klass) {
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
    const { fetchKlasses, setTimeoutActive, setToastMessage } = this.props
    if (!this.props.ui.timeoutActive) {
      setTimeout(() => {
        const { ui } = this.props
        setTimeoutActive(false)
        const deadline = moment(ui.initialTime).add(2, "minutes")
        const now = moment()
        if (now.isBefore(deadline)) {
          fetchKlasses(SETTINGS.user.username)
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
      klasses,
      klassesFinished,
      payableKlassesData,
      selectedKlass,
      showDialog
    } = this.props

    let renderedPayment = null
    let renderedPaymentHistory = null

    if (klassesFinished) {
      renderedPayment = (
        <Payment
          hideDialog={hideDialog}
          showDialog={showDialog}
          ui={ui}
          paymentProcessing={paymentProcessing}
          payableKlassesData={payableKlassesData}
          selectedKlass={selectedKlass}
          now={moment()}
          sendPayment={this.sendPayment}
          setPaymentAmount={this.setPaymentAmount}
          setSelectedKlassKey={this.setSelectedKlassKey}
        />
      )

      const klassDataWithPayments = this.getKlassDataWithPayments(klasses || [])
      renderedPaymentHistory =
        klassDataWithPayments.length > 0 ? (
          <div className="body-row">
            <PaymentHistory klassDataWithPayments={klassDataWithPayments} />
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

const withPayableKlasses = state => {
  return {
    ...state,
    payableKlassesData: R.filter(R.propEq("is_user_eligible_to_pay", true))(
      state.klasses || []
    )
  }
}

const withDerivedSelectedKlass = state => {
  const {
    payableKlassesData,
    ui: { selectedKlassKey }
  } = state

  let selectedKlass
  if (_.isNumber(selectedKlassKey)) {
    selectedKlass = R.find(R.propEq("klass_key", selectedKlassKey))(
      payableKlassesData
    )
  } else if (payableKlassesData.length === 1) {
    selectedKlass = payableKlassesData[0]
  }

  return selectedKlass ? { ...state, selectedKlass: selectedKlass } : state
}

const mapStateToProps = R.compose(
  withDerivedSelectedKlass,
  withPayableKlasses,
  state => ({
    paymentProcessing: R.pathOr(
      false,
      ["queries", "payment", "isPending"],
      state
    ),
    klasses:           R.pathOr([], ["entities", "klasses"], state),
    klassesProcessing: R.pathOr(
      false,
      ["queries", "klasses", "isPending"],
      state
    ),
    klassesFinished: R.pathOr(
      false,
      ["queries", "klasses", "isFinished"],
      state
    ),
    ui: state.ui
  })
)

const mapDispatchToProps = dispatch => ({
  clearUI:      () => dispatch(clearUI()),
  fetchKlasses: (username: string) =>
    dispatch(requestAsync(queries.klasses.klassQuery(username))),
  hideDialog:  (dialogKey: string) => dispatch(hideDialog(dialogKey)),
  sendPayment: (payload: PaymentPayload) =>
    dispatch(mutateAsync(queries.ecommerce.paymentMutation(payload))),
  setPaymentAmount:    (amount: string) => dispatch(setPaymentAmount(amount)),
  setSelectedKlassKey: (klassKey: number) =>
    dispatch(setSelectedKlassKey(klassKey)),
  setToastMessage:  (payload: any) => dispatch(setToastMessage(payload)),
  setTimeoutActive: (active: boolean) => dispatch(setTimeoutActive(active)),
  showDialog:       (dialogKey: string) => dispatch(showDialog(dialogKey))
})

export default connect(mapStateToProps, mapDispatchToProps)(PaymentPage)
