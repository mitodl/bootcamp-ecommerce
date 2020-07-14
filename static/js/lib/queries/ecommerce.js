// @flow
import { objOf } from "ramda"

import { DEFAULT_NON_GET_OPTIONS } from "../redux_query"
import { paymentAPI } from "../urls"
import { nextState } from "./util"

import type { PaymentPayload } from "../../flow/ecommerceTypes"

const orderStatusKey = "orderStatus"

export default {
  paymentMutation: (payload: PaymentPayload) => ({
    queryKey: "payment",
    url:      paymentAPI.toString(),
    options:  {
      ...DEFAULT_NON_GET_OPTIONS
    },
    body: {
      ...payload
    },
    update: {
      payment: () => null
    }
  }),
  orderQuery: (orderId: string) => ({
    queryKey: orderStatusKey,
    url:      `/api/orders/${orderId}/`,
    options:  {
      ...DEFAULT_NON_GET_OPTIONS
    },
    transform: objOf(orderStatusKey),
    update:    {
      [orderStatusKey]: nextState
    },
    force: true
  })
}
