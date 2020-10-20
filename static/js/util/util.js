// @flow
import Decimal from "decimal.js-light"
import * as R from "ramda"
import _ from "lodash"
import moment from "moment"

import {
  BOOTCAMP_RUN_FACET_KEY,
  CS_DEFAULT,
  CS_ERROR_MESSAGES,
  ORDER_FULFILLED,
  REVIEW_STATUS_DISPLAY_MAP,
  STATUS_FACET_KEY
} from "../constants"

import type { BootcampRun } from "../flow/bootcampTypes"
import type { HttpResponse } from "../flow/httpTypes"

/**
 * Creates a POST form with hidden input fields
 * @param url the url for the form action
 * @param payload Each key value pair will become an input field
 */
export function createForm(url: string, payload: Object): HTMLFormElement {
  const form = document.createElement("form")
  form.setAttribute("action", url)
  form.setAttribute("method", "post")
  form.setAttribute("class", "cybersource-payload")

  for (const key: string of Object.keys(payload)) {
    const value = payload[key]
    const input = document.createElement("input")
    input.setAttribute("name", key)
    input.setAttribute("value", value)
    input.setAttribute("type", "hidden")
    form.appendChild(input)
  }
  return form
}

export const isNilOrBlank = R.either(R.isNil, R.isEmpty)

export const formatDollarAmount = (amount: ?number): string => {
  amount = amount || 0
  const formattedAmount = amount.toLocaleString("en-US", {
    style:                 "currency",
    currency:              "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
  return formattedAmount.endsWith(".00") ?
    formattedAmount.substring(0, formattedAmount.length - 3) :
    formattedAmount
}

export const formatReadableDate = (datetime: moment$Moment): string =>
  datetime.format("MMM D, YYYY")

export const formatReadableDateFromStr = (datetimeString: string): string =>
  formatReadableDate(moment(datetimeString))

export const formatStartEndDateStrings = (
  startDtString: ?string,
  endDtString: ?string
): string => {
  let formattedStart, formattedEnd
  if (startDtString) {
    formattedStart = formatReadableDateFromStr(startDtString)
  }
  if (endDtString) {
    formattedEnd = formatReadableDateFromStr(endDtString)
  }
  if (!formattedStart && !formattedEnd) {
    return ""
  } else if (!formattedStart) {
    // $FlowFixMe: This cannot be un-initialized
    return `Ends ${formattedEnd}`
  } else if (!formattedEnd) {
    // $FlowFixMe: This cannot be un-initialized
    return `Starts ${formattedStart}`
  } else {
    return `${formattedStart} - ${formattedEnd}`
  }
}

export const getRunWithFulfilledOrder = (
  runData: ?Array<Object>,
  orderId: number
) =>
  R.find(
    bootcampRun =>
      R.any(
        payment =>
          payment.order.status === ORDER_FULFILLED &&
          payment.order.id === orderId,
        bootcampRun.payments
      ),
    runData
  )

export const getInstallmentDeadlineDates = R.map(
  R.compose(moment, R.prop("deadline"))
)

export function* incrementer(): Generator<number, *, *> {
  let int = 1
  // eslint-disable-next-line no-constant-condition
  while (true) {
    yield int++
  }
}

export const formatTitle = (text: string) => `MIT Bootcamps | ${text}`

export const newSetWith = (set: Set<*>, valueToAdd: any): Set<*> => {
  const newSet = new Set(set)
  newSet.add(valueToAdd)
  return newSet
}

export const newSetWithout = (set: Set<*>, valueToDelete: any): Set<*> => {
  const newSet = new Set(set)
  newSet.delete(valueToDelete)
  return newSet
}

export const formatPrice = (price: ?string | number | Decimal): string => {
  if (price === null || price === undefined) {
    return ""
  } else {
    let decimalPrice: Decimal = Decimal(price).toDecimalPlaces(2)
    let formattedPrice
    const isNegative = decimalPrice.isNegative()
    if (isNegative) {
      decimalPrice = decimalPrice.times(-1)
    }

    if (decimalPrice.isInteger()) {
      formattedPrice = decimalPrice.toFixed(0)
    } else {
      formattedPrice = decimalPrice.toFixed(2, Decimal.ROUND_HALF_UP)
    }

    return `${isNegative ? "-" : ""}$${formattedPrice}`
  }
}

export const getFilenameFromPath = (url: string) =>
  url.substring(url.lastIndexOf("/") + 1)

/*
 * Our uploaded filenames begin with a media path. Until we start saving the
 * raw file names for uploaded files, this utility function can be used to
 * extract the file name.
 * Ex: "media/1/abcde-12345_some_resume.pdf" -> "some_resume.pdf"
 */
export const getFilenameFromMediaPath = R.compose(
  R.join("_"),
  R.tail(),
  R.split("_"),
  R.defaultTo("")
)

export const isErrorStatusCode = (statusCode: number): boolean =>
  statusCode >= 400

export const isErrorResponse = (response: HttpResponse<*>): boolean =>
  isErrorStatusCode(response.status)

export const getResponseBodyErrors = (
  response: HttpResponse<*>
): string | Array<string> | null => {
  if (!response || !response.body || !response.body.errors) {
    return null
  }
  if (Array.isArray(response.body.errors)) {
    return response.body.errors.length === 0 ? null : response.body.errors
  }
  return response.body.errors === "" ? null : response.body.errors
}

export const getFirstResponseBodyError = (
  response: HttpResponse<*>
): ?string => {
  const errors = getResponseBodyErrors(response)
  if (!Array.isArray(errors)) {
    return errors
  }
  return errors.length === 0 ? null : errors[0]
}

export const getXhrResponseError = (response: Object): ?string => {
  if (_.isString(response)) {
    try {
      response = JSON.parse(response)
    } catch (e) {
      return null
    }
  }
  if (!_.isObject(response)) {
    return null
  }
  if (_.isArray(response) && response.length > 0) {
    return response[0]
  }
  if (response.errors && response.errors.length > 0) {
    return response.errors[0]
  }
  if (response.error && response.error !== "") {
    return response.error
  }
  return null
}

export const parsePrice = (priceStr: string | number): Decimal => {
  let price
  try {
    price = new Decimal(priceStr)
  } catch (e) {
    return null
  }
  return price.toDecimalPlaces(2)
}

export const formatRunDateRange = (run: BootcampRun) =>
  `${run.start_date ? formatReadableDateFromStr(run.start_date) : "TBD"} - ${
    run.end_date ? formatReadableDateFromStr(run.end_date) : "TBD"
  }`

export const recoverableErrorCode = (error: string) =>
  error ? error.match(/(CS_101|CS_102)/g) : null

export const transformError = (error: string) =>
  CS_ERROR_MESSAGES[recoverableErrorCode(error) || CS_DEFAULT]
