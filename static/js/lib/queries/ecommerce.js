// @flow
import { getCookie } from "../api"

import type { PaymentPayload } from "../../flow/ecommerceTypes"

const DEFAULT_POST_OPTIONS = {
  headers: {
    "X-CSRFTOKEN": getCookie("csrftoken")
  }
}

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
      ...DEFAULT_POST_OPTIONS
    }
  })
}
