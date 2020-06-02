// @flow
import type { BootcampRun } from "./bootcampTypes"

export type Application = {
  id:           number,
  state:        string,
  created_on:   any,
  bootcamp_run: BootcampRun
}

export type ApplicationRunStep = {
  id:              number,
  due_date:        string,
  step_order:      number,
  submission_type: string
}

export type ApplicationSubmission = {
  id:                      number,
  run_application_step_id: number,
  submitted_date:          ?string,
  review_status:           ?string,
  review_status_date:      ?string
}

export type LegacyOrderPartial = {
  id:               number,
  status:           string,
  created_on:       string,
  updated_on:       string
}

export type ApplicationOrder = {
  total_price_paid: number,
} & LegacyOrderPartial

export type ApplicationDetail = {
  id:                    number,
  state:                 string,
  bootcamp_run:          BootcampRun,
  resume_filename:       ?string,
  linkedin_url:          ?string,
  resume_upload_date:    ?string,
  payment_deadline:      string,
  run_application_steps: Array<ApplicationRunStep>,
  submissions:           Array<ApplicationSubmission>,
  orders:                Array<ApplicationOrder>,
  created_on:            string
}

export type ApplicationDetailState = {
  [string]: ApplicationDetail
}
