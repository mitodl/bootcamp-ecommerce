// @flow
/* global SETTINGS: false */
import React from 'react';
import _ from 'lodash';
import moment from 'moment';

import {
  isNilOrBlank,
  formatDollarAmount,
  formatReadableDate
} from '../util/util';
import type { UIState } from '../reducers';
import type { RestState } from '../rest';
import type { InputEvent } from '../flow/events';

export default class Payment extends React.Component {
  props: {
    ui: UIState,
    payment: RestState,
    payableKlassesData: Array<Object>,
    selectedKlass: Object,
    sendPayment: () => void,
    setPaymentAmount: (event: InputEvent) => void,
    setSelectedKlassKey: (event: InputEvent) => void
  };

  renderKlassDropdown = () => {
    const {
      payableKlassesData,
      ui: { selectedKlassKey },
      setSelectedKlassKey
    } = this.props;

    let options = _.map(
      payableKlassesData,
      (klass) => (<option value={klass.klass_key} key={klass.klass_key}>{ klass.display_title }</option>)
    );
    options.unshift(
      <option value="" key="default" disabled style={{display: 'none'}}>Select...</option>
    );
    let valueProp = selectedKlassKey ?
      {value: selectedKlassKey} :
      {defaultValue: ""};

    return (
      <div className="klass-select-section">
        <p className="desc">
          Which Bootcamp do you want to pay for?
        </p>
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
    );
  };

  renderSelectedKlass = () => {
    const {
      ui: { paymentAmount },
      payment: { processing },
      selectedKlass,
      setPaymentAmount,
      sendPayment
    } = this.props;

    let deadlineDateText;
    if (!_.isEmpty(selectedKlass.payment_deadline)) {
      let deadlineDate = formatReadableDate(moment(selectedKlass.payment_deadline));
      deadlineDateText = `You can pay any amount, but the full payment must be complete by ${deadlineDate}`;
    } else {
      deadlineDateText = 'You can pay any amount toward the total cost.';
    }
    let totalPaid = selectedKlass.total_paid || 0;

    return <div className="klass-display-section">
      <p className="desc">
        You have been accepted to {selectedKlass.display_title}.<br />
        You have paid {formatDollarAmount(totalPaid)} out
        of {formatDollarAmount(selectedKlass.price)}.
      </p>
      <p className="deadline-date">{deadlineDateText}</p>
      <div className="payment">
        <input
          type="number"
          id="payment-amount"
          value={paymentAmount}
          onChange={setPaymentAmount}
          placeholder="Enter amount"
        />
        <button className="btn large-cta" onClick={sendPayment} disabled={processing}>
          Pay Now
        </button>
      </div>
    </div>;
  };

  render() {
    const { payableKlassesData, selectedKlass } = this.props;

    let welcomeMessage = !isNilOrBlank(SETTINGS.user.full_name) ?
      <h1 className="greeting">Hi {SETTINGS.user.full_name}!</h1> :
      null;
    let renderedKlassDropdown = (payableKlassesData.length > 1) ?
      this.renderKlassDropdown() :
      null;
    let renderedSelectedKlass = selectedKlass ?
      this.renderSelectedKlass() :
      null;

    return <div className="payment-section">
      {welcomeMessage}
      {renderedKlassDropdown}
      {renderedSelectedKlass}
    </div>;
  }
}
