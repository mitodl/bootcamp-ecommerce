// @flow
export type PaymentPayload = {
  klass_key: number,
  payment_amount: string,
}

export type PaymentResponse = {
  url: string,
  payload: Object
}
