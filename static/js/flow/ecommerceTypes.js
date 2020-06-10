// @flow
export type PaymentPayload = {
  application_id: number,
  payment_amount: string,
}

export type PaymentResponse = {
  url: string,
  payload: Object
}
