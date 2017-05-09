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
  setSelectedKlassKey
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
    payableKlassesData: Array<Object>,
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

  setSelectedKlassKey = (event: InputEvent) => {
    const { dispatch } = this.props;
    dispatch(setSelectedKlassKey(parseInt(event.target.value)));
  };

  getKlassDataWithPayments = R.filter(
    R.compose(
      R.not,
      R.equals(0),
      R.propOr(0, 'total_paid')
    )
  );

  render() {
    const {
      ui,
      payment,
      klasses,
      payableKlassesData,
      selectedKlass
    } = this.props;

    let klassDataWithPayments = this.getKlassDataWithPayments(klasses.data || []);
    let renderedPaymentHistory = klassDataWithPayments.length > 0
      ? (
        <div className="body-row">
          <PaymentHistory klassDataWithPayments={klassDataWithPayments} />
        </div>
      )
      : null;

    return <div>
      <div className="body-row top-content-container">
        <div className="top-content">
          <Payment
            ui={ui}
            payment={payment}
            payableKlassesData={payableKlassesData}
            selectedKlass={selectedKlass}
            sendPayment={this.sendPayment}
            setPaymentAmount={this.setPaymentAmount}
            setSelectedKlassKey={this.setSelectedKlassKey}
          />
        </div>
      </div>
      { renderedPaymentHistory }
    </div>;
  }
}

const withPayableKlasses = state => {
  return {
    ...state,
    payableKlassesData: R.filter(
      R.propEq('is_user_eligible_to_pay', true)
    )(state.klasses.data || [])
  };
};

const withDerivedSelectedKlass = state => {
  let {
    payableKlassesData,
    ui: { selectedKlassKey }
  } = state;

  let selectedKlass;
  if (_.isNumber(selectedKlassKey)) {
    selectedKlass = R.find(
      R.propEq('klass_key', selectedKlassKey)
    )(payableKlassesData);
  }
  else if (payableKlassesData.length === 1) {
    selectedKlass = payableKlassesData[0];
  }

  return selectedKlass
    ? { ...state, selectedKlass: selectedKlass }
    : state;
};

const mapStateToProps = R.compose(
  withDerivedSelectedKlass,
  withPayableKlasses,
  (state) => ({
    payment: state.payment,
    klasses: state.klasses,
    ui: state.ui
  })
);

export default connect(mapStateToProps)(PaymentPage);
