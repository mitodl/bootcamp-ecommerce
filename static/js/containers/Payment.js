// @flow
/* global SETTINGS: false */
import React from 'react';
import { connect } from 'react-redux';
import type { Dispatch } from 'redux';

import type {
  UIState,
} from '../reducers';
import {
  setTotal,
} from '../actions';
import { actions } from '../rest';
import type { RestState } from '../rest';

class Payment extends React.Component {
  props: {
    ui: UIState,
    payment: RestState,
    dispatch: Dispatch,
  };

  sendPayment = () => {
    const { dispatch, ui: { total } } = this.props;
    dispatch(actions.payment(total));
  };

  setTotal = (event) => {
    const { dispatch } = this.props;
    dispatch(setTotal(event.target.value));
  };

  render() {
    const {
      ui: { total },
      payment: { processing },
    } = this.props;

    return <div className="payment">
      <h3 className="intro">{SETTINGS.full_name}, Welcome to MIT Bootcamps</h3>
      <h2 className="bootcamp-title">Internet of Things</h2>
      <span>You have paid $2000 out of $6000</span>
      <div className="payment">
        <span>Make a payment of:</span>
        <span>
          $<input type="number" id="total" value={total} onChange={this.setTotal} />
        </span>
        <button className="payment-button" onClick={this.sendPayment} disabled={processing}>
          Pay
        </button>
      </div>

      <a href="#">Print your statement</a>
    </div>;
  }
}

const mapStateToProps = state => {
  return {
    payment: state.payment,
    ui: state.ui,
  };
};

export default connect(mapStateToProps)(Payment);
