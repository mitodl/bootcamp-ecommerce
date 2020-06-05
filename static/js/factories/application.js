// @flow
import casual from "casual-browserify"
import moment from "moment"
import { sum } from "ramda"

import { generateFakeRun, generateOrder } from "./index"
import { incrementer } from "../util/util"
import { APP_STATE_TEXT_MAP } from "../constants"

import type { Application, ApplicationDetail } from "../flow/applicationTypes"

const incr = incrementer()

export const makeApplication = (): Application => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id:           incr.next().value,
  state:        casual.random_element(Object.keys(APP_STATE_TEXT_MAP)),
  created_on:   moment().format(),
  bootcamp_run: generateFakeRun()
})

export const makeApplicationDetail = (): ApplicationDetail => {
  const run = generateFakeRun()
  // take off 10% to simulate a personal price
  const price =
    sum(run.installments.map(installment => installment.amount)) * 0.9
  return {
    // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
    id:                    incr.next().value,
    state:                 casual.random_element(Object.keys(APP_STATE_TEXT_MAP)),
    bootcamp_run:          run,
    resume_filename:       `${casual.word}.${casual.file_extension}`,
    linkedin_url:          casual.url,
    resume_upload_date:    moment().format(),
    payment_deadline:      moment().format(),
    run_application_steps: [],
    submissions:           [],
    orders:                [generateOrder()],
    created_on:            moment().format(),
    price:                 price
  }
}
