import _ from "lodash"
import moment from "moment"
import casual from "casual-browserify"

import type { BootcampRun, BootcampRunPage } from "../flow/bootcampTypes"
import { incrementer } from "../util/util"

const incr = incrementer()

export const generateFakeRunPage = (): BootcampRunPage => ({
  description:         casual.text,
  subhead:             casual.text,
  thumbnail_image_src: casual.url
})

export const generateFakeRun = (): BootcampRun => ({
  id:            incr.next().value,
  display_title: casual.title,
  title:         casual.title,
  run_key:       casual.word,
  start_date:    moment().format(),
  end_date:      moment().format(),
  page:          generateFakeRunPage(),
  bootcamp:      {
    id:    incr.next().value,
    title: casual.title
  }
})

export const generateFakePayableRuns = (
  numRuns = 1,
  { hasInstallment = true, hasPayment = false } = {}
) => {
  return _.times(numRuns, i => {
    const runKey = i + 1
    return {
      bootcamp_run_name: `Bootcamp Run ${i}`,
      display_title:     `Bootcamp Run ${i}`,
      run_key:           runKey,
      payment_deadline:  moment(),
      total_paid:        hasPayment ? 100 : 0,
      price:             1000,
      payments:          hasPayment ? [generateFakePayment({ runKey: runKey })] : [],
      installments:      hasInstallment ? [generateFakeInstallment()] : []
    }
  })
}

export const generateFakePayment = ({ runKey = 1, price = 100 } = {}) => ({
  order: {
    id:         runKey + 100,
    status:     "fulfilled",
    created_on: "2017-05-09T13:57:20.414821Z",
    updated_on: "2017-05-09T15:54:54.232055Z"
  },
  run_key:     runKey,
  description: `Installment for Bootcamp Run ${runKey}`,
  price:       price
})

export const generateFakeInstallment = ({
  deadline = undefined,
  amount = 100
} = {}) => ({
  amount:   amount,
  deadline: deadline || moment().format()
})
