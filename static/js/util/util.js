// @flow
import R from 'ramda';
import moment from 'moment';

import { ORDER_FULFILLED } from '../constants';

/**
 * Creates a POST form with hidden input fields
 * @param url the url for the form action
 * @param payload Each key value pair will become an input field
 */
export function createForm(url: string, payload: Object): HTMLFormElement {
  const form = document.createElement("form");
  form.setAttribute("action", url);
  form.setAttribute("method", "post");
  form.setAttribute("class", "cybersource-payload");

  for (let key: string of Object.keys(payload)) {
    const value = payload[key];
    const input = document.createElement("input");
    input.setAttribute("name", key);
    input.setAttribute("value", value);
    input.setAttribute("type", "hidden");
    form.appendChild(input);
  }
  return form;
}

export const isNilOrBlank = R.either(R.isNil, R.isEmpty);

export const formatDollarAmount = (amount: ?number): string => {
  amount = amount || 0;
  let formattedAmount = amount.toLocaleString('en-US', {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  return formattedAmount.endsWith(".00")
    ? formattedAmount.substring(0, formattedAmount.length - 3)
    : formattedAmount;
};

export const formatReadableDate = (datetime: moment$Moment): string => (
  datetime.format("MMM D, YYYY")
);

export const formatReadableDateFromStr = (datetimeString: string): string => (
  formatReadableDate(moment(datetimeString))
);

export const getKlassWithFulfilledOrder = (klassData: ?Array<Object>, orderId: number) => (
  R.find(
    klass => R.any(
      payment => payment.order.status === ORDER_FULFILLED && payment.order.id === orderId,
      klass.payments,
    ),
    klassData,
  )
);

export const getInstallmentDeadlineDates = R.map(
  R.compose(
    moment,
    R.prop('deadline')
  )
);
