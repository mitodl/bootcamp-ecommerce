// @flow
import {
  SUBMISSION_VIDEO,
  SUBMISSION_QUIZ,
  REVIEW_STATUS_APPROVED,
  REVIEW_STATUS_REJECTED,
  REVIEW_STATUS_PENDING
} from "../constants"

import type { BootcampRun } from "./bootcampTypes"

export type Application = {
  id:           number,
  state:        string,
  created_on:   any,
  bootcamp_run: BootcampRun
}

export type ValidAppStepType = SUBMISSION_VIDEO | SUBMISSION_QUIZ

export type ApplicationRunStep = {
  id:              number,
  due_date:        string,
  step_order:      number,
  submission_type: ValidAppStepType
}

export type ValidReviewStatusType = REVIEW_STATUS_APPROVED | REVIEW_STATUS_REJECTED | REVIEW_STATUS_PENDING

export type ApplicationSubmission = {
  id:                      number,
  run_application_step_id: number,
  submitted_date:          ?string,
  review_status:           ValidReviewStatusType,
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
  is_paid_in_full:       boolean,
  run_application_steps: Array<ApplicationRunStep>,
  submissions:           Array<ApplicationSubmission>,
  orders:                Array<ApplicationOrder>,
  created_on:            string,
  price:                 number,
}

export type ApplicationDetailState = {
  [string]: ApplicationDetail
}
