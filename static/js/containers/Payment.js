// @flow
/* global SETTINGS: false */
import React from 'react';
import { connect } from 'react-redux';
import type { Dispatch } from 'redux';
import _ from 'lodash';

import type {
  UIState,
} from '../reducers';
import {
  clearUI,
  setPaymentAmount,
  setSelectedKlassIndex
} from '../actions';
import { actions } from '../rest';
import type { RestState } from '../rest';
import { createForm, isNilOrBlank } from '../util/util';

class Payment extends React.Component {
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
    dispatch(
      actions.payment({
        paymentAmount: paymentAmount,
        klassId: selectedKlass.klass_id
      })
    ).then(result => {
      const { url, payload } = result;
      const form = createForm(url, payload);
      const body = document.querySelector("body");
      body.appendChild(form);
      form.submit();
    });
  };

  setPaymentAmount = (event) => {
    const { dispatch } = this.props;
    dispatch(setPaymentAmount(event.target.value));
  };

  setSelectedKlassIndex = (event) => {
    const { dispatch } = this.props;
    dispatch(setSelectedKlassIndex(parseInt(event.target.value)));
  };

  renderKlassDropdown = () => {
    const {
      klasses,
      ui: { selectedKlassIndex }
    } = this.props;

    let options = _.map(
      klasses.data,
      (klass, i) => (<option value={i} key={i}>{ klass.klass_name }</option>)
    );
    options.unshift(
      <option value="" key="default" disabled style={{display: 'none'}}>Select...</option>
    );
    let valueProp = selectedKlassIndex ?
      {value: selectedKlassIndex} :
      {defaultValue: ""};

    return (
      <select
        className="klass-select"
        onChange={this.setSelectedKlassIndex}
        {...valueProp}
      >
        {options}
      </select>
    );
  };

  renderSelectedKlass() {
    const {
      ui: { paymentAmount },
      payment: { processing },
      selectedKlass
    } = this.props;

    return <div>
      <h2 className="klass-title">{selectedKlass.klass_name}</h2>
      <span>You have paid ${selectedKlass.total_paid} out of ${selectedKlass.price}</span>
      <div className="payment">
        <span>Make a payment of:</span>
        <span>
          $<input type="number" id="payment-amount" value={paymentAmount} onChange={this.setPaymentAmount}/>
        </span>
        <button className="payment-button" onClick={this.sendPayment} disabled={processing}>
          Pay
        </button>
      </div>
      <a href="#">Print your statement</a>
    </div>;
  }

  render() {
    const { klasses, selectedKlass } = this.props;

    let welcomeMessage = "Welcome to MIT Bootcamps";
    if (!isNilOrBlank(SETTINGS.user.full_name)) {
      welcomeMessage = `${SETTINGS.user.full_name}, ${welcomeMessage}`;
    }
    let renderedKlassDropdown = (klasses.data && klasses.data.length > 1) ?
      this.renderKlassDropdown() :
      null;
    let renderedSelectedKlass = selectedKlass ?
      this.renderSelectedKlass() :
      null;

    return <div className="payment">
      <h3 className="intro">{welcomeMessage}</h3>
      {renderedKlassDropdown}
      {renderedSelectedKlass}
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
  return klassesExist && _.isNumber(selectedKlassIndex) ?
    klasses.data[selectedKlassIndex] :
    undefined;
};

const mapStateToProps = state => {
  return {
    payment: state.payment,
    klasses: state.klasses,
    ui: state.ui,
    selectedKlass: deriveSelectedKlass(state),
  };
};

export default connect(mapStateToProps)(Payment);
