// @flow
export type PaymentPayload = {
  run_key: number,
  payment_amount: string,
}

export type PaymentResponse = {
  url: string,
  payload: Object
}
