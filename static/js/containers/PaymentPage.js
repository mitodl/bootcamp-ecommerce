// @flow
/* global SETTINGS: false */
import React from "react"
import { connect } from "react-redux"
import type { Dispatch } from "redux"
import _ from "lodash"
import R from "ramda"
import URI from "urijs"
import moment from "moment"

import {
  clearUI,
  setPaymentAmount,
  setSelectedKlassKey,
  setTimeoutActive,
  setToastMessage,
  FETCH_SUCCESS
} from "../actions"
import { TOAST_SUCCESS, TOAST_FAILURE } from "../constants"
import { actions } from "../rest"
import { createForm, getKlassWithFulfilledOrder } from "../util/util"
import Payment from "../components/Payment"
import PaymentHistory from "../components/PaymentHistory"
import Toast from "../components/Toast"
import type { UIState } from "../reducers"
import type { RestState } from "../rest"
import type { InputEvent } from "../flow/events"

class PaymentPage extends React.Component {
  props: {
    dispatch: Dispatch,
    ui: UIState,
    payment: RestState,
    klasses: RestState,
    payableKlassesData: Array<Object>,
    selectedKlass: Object
  }

  fetchAPIdata() {
    this.fetchKlasses()
  }

  componentDidMount() {
    this.fetchAPIdata()
    this.handleOrderStatus()
  }

  componentDidUpdate() {
    this.fetchAPIdata()
    this.handleOrderStatus()
  }

  componentWillUnmount() {
    const { dispatch } = this.props
    dispatch(clearUI())
  }

  fetchKlasses() {
    const { dispatch, klasses } = this.props
    if (!klasses.fetchStatus) {
      dispatch(actions.klasses({ username: SETTINGS.user.username }))
    }
  }

  sendPayment = () => {
    const { dispatch, ui: { paymentAmount }, selectedKlass } = this.props
    if (selectedKlass && paymentAmount) {
      dispatch(
        actions.payment({
          paymentAmount: paymentAmount,
          klassKey:      selectedKlass.klass_key
        })
      ).then(result => {
        const { url, payload } = result
        const form = createForm(url, payload)
        const body = document.querySelector("body")
        body.appendChild(form)
        form.submit()
      })
    }
  }

  setPaymentAmount = (event: InputEvent) => {
    const { dispatch } = this.props
    dispatch(setPaymentAmount(event.target.value))
  }

  setSelectedKlassKey = (event: InputEvent) => {
    const { dispatch } = this.props
    dispatch(setSelectedKlassKey(parseInt(event.target.value)))
  }

  getKlassDataWithPayments = R.filter(
    R.compose(R.not, R.equals(0), R.propOr(0, "total_paid"))
  )

  handleOrderStatus = (): void => {
    const { klasses } = this.props
    const query = new URI().query(true)
    if (!klasses.loaded) {
      // wait until we have access to the klasses
      return
    }

    const status = query.status
    if (status === "receipt") {
      const orderId = parseInt(query.order)
      const klass = getKlassWithFulfilledOrder(klasses.data, orderId)
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
    const { dispatch, ui: { toastMessage } } = this.props
    if (toastMessage === null) {
      dispatch(
        setToastMessage({
          title: "Payment Complete!",
          icon:  TOAST_SUCCESS
        })
      )
    }
    window.history.pushState({}, null, new URI().query({}).toString())
  }

  handleOrderPending = (): void => {
    const { dispatch } = this.props
    if (!this.props.ui.timeoutActive) {
      setTimeout(() => {
        const { ui } = this.props
        dispatch(setTimeoutActive(false))
        const deadline = moment(ui.initialTime).add(2, "minutes")
        const now = moment()
        if (now.isBefore(deadline)) {
          dispatch(actions.klasses({ username: SETTINGS.user.username }))
        } else {
          dispatch(
            setToastMessage({
              message: "Order was not processed",
              icon:    TOAST_FAILURE
            })
          )
        }
      }, 3000)
      dispatch(setTimeoutActive(true))
    }
  }

  handleOrderCancellation = (): void => {
    const { dispatch, ui: { toastMessage } } = this.props

    if (toastMessage === null) {
      dispatch(
        setToastMessage({
          message: "Order was cancelled",
          icon:    TOAST_FAILURE
        })
      )
    }
    window.history.pushState({}, null, new URI().query({}).toString())
  }

  clearMessage = (): void => {
    const { dispatch } = this.props
    dispatch(setToastMessage(null))
  }

  renderToast() {
    const { ui: { toastMessage } } = this.props
    if (!toastMessage) {
      return null
    }

    const {
      icon: iconName,
      title: titleText,
      message: messageText
    } = toastMessage

    let icon
    if (iconName) {
      icon = (
        <i className="material-icons" key="icon">
          {iconName}
        </i>
      )
    }

    let title, message
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
      ui,
      payment,
      klasses,
      payableKlassesData,
      selectedKlass
    } = this.props

    let renderedPayment = null,
      renderedPaymentHistory = null

    if (klasses.fetchStatus === FETCH_SUCCESS) {
      renderedPayment = (
        <Payment
          ui={ui}
          payment={payment}
          payableKlassesData={payableKlassesData}
          selectedKlass={selectedKlass}
          now={moment()}
          sendPayment={this.sendPayment}
          setPaymentAmount={this.setPaymentAmount}
          setSelectedKlassKey={this.setSelectedKlassKey}
        />
      )

      const klassDataWithPayments = this.getKlassDataWithPayments(
        klasses.data || []
      )
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
      state.klasses.data || []
    )
  }
}

const withDerivedSelectedKlass = state => {
  const { payableKlassesData, ui: { selectedKlassKey } } = state

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
    payment: state.payment,
    klasses: state.klasses,
    ui:      state.ui
  })
)

export default connect(mapStateToProps)(PaymentPage)
