// @flow
import _ from "lodash"
import moment from "moment"
import casual from "casual-browserify"

import type {
  BootcampRun,
  BootcampRunPage,
  Installment,
  PayableBootcampRun,
  Payment
} from "../flow/bootcampTypes"
import { incrementer } from "../util/util"
import { ORDER_FULFILLED } from "../constants"
import type {
  ApplicationOrder,
  LegacyOrderPartial
} from "../flow/applicationTypes"

const incr = incrementer()

export const generateFakeRunPage = (): BootcampRunPage => ({
  description:         casual.text,
  subhead:             casual.text,
  thumbnail_image_src: casual.url
})

export const generateFakeRun = (): BootcampRun => ({
  // $FlowFixMe: this should always be a number, but flow doesn't know that
  id:            incr.next().value,
  display_title: casual.title,
  title:         casual.title,
  run_key:       casual.word,
  start_date:    moment().format(),
  end_date:      moment()
    .add(1, "days")
    .format(),
  page:     generateFakeRunPage(),
  bootcamp: {
    // $FlowFixMe: this should always be a number, but flow doesn't know that
    id:    incr.next().value,
    title: casual.title
  },
  installments: _.times(2).map(() => generateFakeInstallment())
})

export const generateFakePayableRuns = (
  numRuns: number = 1,
  {
    hasInstallment = true,
    hasPayment = false
  }: { hasInstallment: boolean, hasPayment: boolean } = {}
): Array<PayableBootcampRun> =>
  _.times(numRuns, i => ({
    bootcamp_run_name: `Bootcamp Run ${i}`,
    display_title:     `Bootcamp Run ${i}`,
    run_key:           i + 1,
    start_date:        moment().format(),
    end_date:          moment()
      .add(1, "days")
      .format(),
    total_paid:   hasPayment ? 100 : 0,
    price:        1000,
    payments:     hasPayment ? [generateFakePayment({ runKey: i + 1 })] : [],
    installments: hasInstallment ? [generateFakeInstallment()] : []
  }))

export const generateLegacyOrderPartial = (): LegacyOrderPartial => ({
  // $FlowFixMe: flow thinks that this may be undefined, but it won't ever be
  id:         incr.next().value,
  status:     ORDER_FULFILLED,
  created_on: moment()
    .add(-3, "days")
    .format(),
  updated_on: moment()
    .add(-3, "days")
    .format()
})

export const generateOrder = (): ApplicationOrder => ({
  ...generateLegacyOrderPartial(),
  total_price_paid: 10
})

export const generateFakePayment = ({
  runKey = 1,
  price = 100
}: { runKey?: number, price?: number } = {}): Payment => ({
  order:       generateLegacyOrderPartial(),
  run_key:     runKey,
  description: `Installment for Bootcamp Run ${runKey}`,
  price:       price
})

export const generateFakeInstallment = ({
  deadline = moment()
    .add(1, "days")
    .format(),
  amount = 100
}: Installment = {}) => ({
  amount:   amount,
  deadline: deadline || moment().format()
})
