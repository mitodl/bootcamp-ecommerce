// @flow
import casual from "casual-browserify"
import moment from "moment"
import { sum } from "ramda"

import { generateFakeRun, generateOrder } from "./index"
import { makeUser } from "./user"
import { incrementer } from "../util/util"
import {
  APP_STATE_TEXT_MAP,
  REVIEW_STATUS_TEXT_MAP,
  REVIEW_STATUS_APPROVED,
  REVIEW_STATUS_PENDING,
  REVIEW_STATUS_REJECTED,
  SUBMISSION_QUIZ,
  SUBMISSION_VIDEO
} from "../constants"
import { makeUser } from "./user"

import type {
  Application,
  ApplicationDetail,
  ApplicationRunStep,
  ApplicationSubmission,
  SubmissionReview,
  ValidAppStepType
} from "../flow/applicationTypes"

const incr = incrementer()
const stepIncr = incrementer()

export const makeApplication = (): Application => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  state: casual.random_element(Object.keys(APP_STATE_TEXT_MAP)),
  created_on: moment().format(),
  bootcamp_run: generateFakeRun()
})

export const makeApplicationRunStep = (
  submissionType?: ValidAppStepType
): ApplicationRunStep => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  due_date: moment().format(),
  // $FlowFixMe
  step_order: stepIncr.next().value,
  submission_type:
    submissionType || casual.random_element([SUBMISSION_VIDEO, SUBMISSION_QUIZ])
})

export const makeApplicationSubmission = (): ApplicationSubmission => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  // $FlowFixMe
  run_application_step_id: incr.next().value,
  submitted_date: moment().format(),
  review_status: casual.random_element([
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_PENDING
  ]),
  review_status_date: moment().format()
})

export const setSubmissionToPending = (
  submission: ApplicationSubmission
): ApplicationSubmission => {
  submission.review_status = REVIEW_STATUS_PENDING
  submission.submitted_date = moment().format()
  submission.review_status_date = undefined
  return submission
}

export const setSubmissionToApproved = (
  submission: ApplicationSubmission
): ApplicationSubmission => {
  submission.review_status = REVIEW_STATUS_APPROVED
  submission.submitted_date = moment().format()
  submission.review_status_date = submission.submitted_date
  return submission
}

export const makeApplicationDetail = (): ApplicationDetail => {
  const run = generateFakeRun()
  // take off 10% to simulate a personal price
  const price =
    sum(run.installments.map(installment => installment.amount)) * 0.9
  return {
    // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
    id: incr.next().value,
    state: casual.random_element(Object.keys(APP_STATE_TEXT_MAP)),
    bootcamp_run: run,
    resume_filepath: casual.url,
    linkedin_url: casual.url,
    resume_upload_date: moment().format(),
    payment_deadline: moment().format(),
    is_paid_in_full: false,
    run_application_steps: [makeApplicationRunStep(), makeApplicationRunStep()],
    submissions: [],
    orders: [generateOrder()],
    created_on: moment().format(),
    price: price,
    user: makeUser()
  }
}

export const setToAwaitingResume = (
  appDetail: ApplicationDetail
): ApplicationDetail => {
  appDetail.resume_upload_date = undefined
  appDetail.resume_filepath = undefined
  appDetail.linkedin_url = undefined
  appDetail.submissions = []
  return appDetail
}

export const setToAwaitingSubmission = (
  appDetail: ApplicationDetail
): ApplicationDetail => {
  appDetail = setToAwaitingResume(appDetail)
  appDetail.resume_upload_date = moment().format()
  appDetail.resume_filepath = casual.url
  appDetail.submissions = []
  return appDetail
}

export const setToAwaitingReview = (
  appDetail: ApplicationDetail
): ApplicationDetail => {
  appDetail = setToAwaitingSubmission(appDetail)
  let submission = makeApplicationSubmission()
  submission = setSubmissionToPending(submission)
  submission.run_application_step_id = appDetail.run_application_steps[0].id
  appDetail.submissions = [submission]
  return appDetail
}

export const setToAwaitingPayment = (
  appDetail: ApplicationDetail
): ApplicationDetail => {
  appDetail = setToAwaitingSubmission(appDetail)
  appDetail.is_paid_in_full = false
  for (let i = 0; i < appDetail.run_application_steps.length; i++) {
    let submission = makeApplicationSubmission()
    submission = setSubmissionToApproved(submission)
    submission.run_application_step_id = appDetail.run_application_steps[i].id
    appDetail.submissions = appDetail.submissions.concat(submission)
  }
  return appDetail
}

export const setToPaid = (appDetail: ApplicationDetail): ApplicationDetail => {
  appDetail = setToAwaitingPayment(appDetail)
  appDetail.is_paid_in_full = true
  return appDetail
}

export const makeSubmissionReview = (): SubmissionReview => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  run_application_step_id: casual.integer,
  submitted_date: moment().format(),
  review_status: casual.random_element(Object.keys(REVIEW_STATUS_TEXT_MAP)),
  review_status_date: moment().format(),
  bootcamp_application: makeApplication(),
  learner: makeUser(),
  interview_url: casual.url
})
