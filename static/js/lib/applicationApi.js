import * as R from "ramda"

import { ORDER_STATUS_FAILED, ORDER_STATUS_FULFILLED } from "../constants"
import { isErrorResponse } from "../util/util"

import type { Application, ApplicationDetail } from "../flow/applicationTypes"
import type { HttpResponse } from "../flow/httpTypes"
import type { OrderResponse } from "../flow/ecommerceTypes"

export const calcOrderBalances = (application: ApplicationDetail) => {
  const sortedOrders = R.sortBy(order => order.updated_on, application.orders)
  let balance = application.price
  const ordersAndBalances = sortedOrders.map(order => {
    balance -= order.total_price_paid
    return { order, balance }
  })
  const totalPaid = R.sum(sortedOrders.map(order => order.total_price_paid))
  const totalPrice = application.price

  return {
    ordersAndBalances,
    totalPaid,
    totalPrice,
    balanceRemaining: balance
  }
}

export const isStatusPollingFinished = (
  response: HttpResponse<OrderResponse>
): boolean =>
  isErrorResponse(response) ||
  !!(
    response.body &&
    response.body.status &&
    [ORDER_STATUS_FULFILLED, ORDER_STATUS_FAILED].includes(response.body.status)
  )

export const findAppByRunTitle = (
  applications: Array<Application>,
  bootcampRunTitle: string
): ?Application => {
  return applications.find(
    (application: Application) =>
      application.bootcamp_run.title === bootcampRunTitle
  )
}