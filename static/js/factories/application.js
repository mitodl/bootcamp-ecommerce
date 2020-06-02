// @flow
import casual from "casual-browserify"
import moment from "moment"

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

export const makeApplicationDetail = (): ApplicationDetail => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id:                    incr.next().value,
  state:                 casual.random_element(Object.keys(APP_STATE_TEXT_MAP)),
  bootcamp_run:          generateFakeRun(),
  resume_filename:       `${casual.word}.${casual.file_extension}`,
  linkedin_url:          casual.url,
  resume_upload_date:    moment().format(),
  payment_deadline:      moment().format(),
  run_application_steps: [],
  submissions:           [],
  orders:                [generateOrder()],
  created_on:            moment().format()
})
