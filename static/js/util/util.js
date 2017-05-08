// @flow
import R from 'ramda';

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
  return amount.toLocaleString('en-US', {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  });
};
