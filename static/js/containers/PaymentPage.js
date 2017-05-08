// @flow
/* global SETTINGS: false */
import React from 'react';
import { connect } from 'react-redux';
import type { Dispatch } from 'redux';
import _ from 'lodash';
import R from 'ramda';

import {
  clearUI,
  setPaymentAmount,
  setSelectedKlassIndex
} from '../actions';
import { actions } from '../rest';
import { createForm } from '../util/util';
import Payment from '../components/Payment';
import PaymentHistory from '../components/PaymentHistory';
import type { UIState } from '../reducers';
import type { RestState } from '../rest';
import type { InputEvent } from '../flow/events';

class PaymentPage extends React.Component {
  props: {
    dispatch: Dispatch,
    ui: UIState,
    payment: RestState,
    klasses: RestState,
    selectedKlass: Object,
  };

  fetchAPIdata() {
    this.fetchKlasses();
  }

  componentDidMount() {
    this.fetchAPIdata();
  }

  componentDidUpdate() {
    this.fetchAPIdata();
  }

  componentWillUnmount() {
    const { dispatch } = this.props;
    dispatch(clearUI());
  }

  fetchKlasses() {
    const { dispatch, klasses } = this.props;
    if (!klasses.fetchStatus) {
      dispatch(
        actions.klasses({username: SETTINGS.user.username})
      );
    }
  }

  sendPayment = () => {
    const {
      dispatch,
      ui: { paymentAmount },
      selectedKlass
    } = this.props;
    if (selectedKlass && paymentAmount) {
      dispatch(
        actions.payment({
          paymentAmount: paymentAmount,
          klassKey: selectedKlass.klass_key
        })
      ).then(result => {
        const {url, payload} = result;
        const form = createForm(url, payload);
        const body = document.querySelector("body");
        body.appendChild(form);
        form.submit();
      });
    }
  };

  setPaymentAmount = (event: InputEvent) => {
    const { dispatch } = this.props;
    dispatch(setPaymentAmount(event.target.value));
  };

  setSelectedKlassIndex = (event: InputEvent) => {
    const { dispatch } = this.props;
    dispatch(setSelectedKlassIndex(parseInt(event.target.value)));
  };

  hasPastPayments = () => {
    const { klasses } = this.props;

    if (!klasses.data) return false;

    let totalPaid = R.compose(
      R.sum,
      R.map(
        R.propOr(0, 'total_paid')
      )
    )(klasses.data);
    return totalPaid > 0;
  };

  render() {
    const {
      ui,
      payment,
      klasses,
      selectedKlass
    } = this.props;

    let renderedPaymentHistory = this.hasPastPayments()
      ? (
        <div className="body-row">
          <PaymentHistory klasses={klasses} />
        </div>
      )
      : null;

    return <div>
      <div className="body-row top-content-container">
        <div className="top-content">
          <Payment
            ui={ui}
            payment={payment}
            klasses={klasses}
            selectedKlass={selectedKlass}
            sendPayment={this.sendPayment}
            setPaymentAmount={this.setPaymentAmount}
            setSelectedKlassIndex={this.setSelectedKlassIndex}
          />
        </div>
      </div>
      { renderedPaymentHistory }
    </div>;
  }
}

const deriveSelectedKlass = state => {
  let {
    klasses,
    ui: { selectedKlassIndex }
  } = state;

  let klassesExist = klasses.data && klasses.data.length > 0;
  // If there's only one klass available, set selectedKlassIndex such that the one klass
  // will be set as the selected klass.
  if (klassesExist && klasses.data.length === 1) {
    selectedKlassIndex = 0;
  }
  return klassesExist && _.isNumber(selectedKlassIndex)
    ? klasses.data[selectedKlassIndex]
    : undefined;
};

const mapStateToProps = state => {
  return {
    payment: state.payment,
    klasses: state.klasses,
    ui: state.ui,
    selectedKlass: deriveSelectedKlass(state),
  };
};

export default connect(mapStateToProps)(PaymentPage);
