// @flow
export type PaymentPayload = {
  application_id: number,
  payment_amount: string,
};

export type PaymentResponse = {
  url: string,
  payload: Object,
};

export type OrderResponse = {
  id: number,
  status: string,
  application_id: number,
  created_on: string,
  updated_on: string,
};

export type CybersourcePayload = {
  decision: string,
  bootcamp_run_purchased: string,
  purchase_date_utc: string,
};
