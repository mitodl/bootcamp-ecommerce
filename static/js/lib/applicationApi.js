/* global SETTINGS: false */
import * as R from "ramda"

import { ORDER_STATUS_FAILED, ORDER_STATUS_FULFILLED } from "../constants"
import { isErrorResponse } from "../util/util"

import type { User } from "../flow/authTypes"
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

export const isNovoEdEnrolled = (application: Application): boolean =>
  !!application.bootcamp_run.novoed_course_stub &&
  !!SETTINGS.novoed_base_url &&
  !!application.enrollment &&
  !!application.enrollment.novoed_sync_date

export const isEligibleToSkipSteps = (
  currentUser: User,
  application: Application
): boolean =>
  currentUser.profile &&
  currentUser.profile.can_skip_application_steps === true &&
  application.bootcamp_run.allows_skipped_steps === true
