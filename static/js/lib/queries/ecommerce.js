// @flow
import { DEFAULT_NON_GET_OPTIONS } from "../redux_query"

import type { PaymentPayload } from "../../flow/ecommerceTypes"

export default {
  paymentMutation: (payload: PaymentPayload) => ({
    queryKey: "payment",
    url:      "/api/v0/payment/",
    update:   {
      payment: () => null
    },
    body: {
      ...payload
    },
    options: {
      ...DEFAULT_NON_GET_OPTIONS
    }
  })
}
