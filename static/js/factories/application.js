// @flow
import casual from "casual-browserify";
import moment from "moment";
import { sum } from "ramda";

import {
  generateFakeRun,
  generateOrder,
  generateFakeEnrollment,
} from "./index";
import { incrementer } from "../util/util";
import {
  APP_STATE_TEXT_MAP,
  REVIEW_STATUS_TEXT_MAP,
  REVIEW_STATUS_APPROVED,
  REVIEW_STATUS_PENDING,
  REVIEW_STATUS_REJECTED,
  REVIEW_STATUS_WAITLISTED,
  SUBMISSION_QUIZ,
  SUBMISSION_VIDEO,
  SUBMISSION_STATUS_TEXT_MAP,
} from "../constants";
import { makeUser } from "./user";

import type {
  Application,
  ApplicationDetail,
  ApplicationRunStep,
  ApplicationSubmission,
  SubmissionReview,
  ValidAppStepType,
  SubmissionFacetData,
} from "../flow/applicationTypes";

const incr = incrementer();
const stepIncr = incrementer();

export const makeApplication = (): Application => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  state: casual.random_element(Object.keys(APP_STATE_TEXT_MAP)),
  certificate_link: casual.url,
  created_on: moment().format(),
  bootcamp_run: generateFakeRun(),
  enrollment: generateFakeEnrollment(),
  has_payments: casual.boolean,
});

export const makeApplicationRunStep = (
  submissionType?: ValidAppStepType,
): ApplicationRunStep => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  due_date: moment().format(),
  // $FlowFixMe
  step_order: stepIncr.next().value,
  submission_type:
    submissionType ||
    casual.random_element([SUBMISSION_VIDEO, SUBMISSION_QUIZ]),
});

export const makeApplicationSubmission = (): ApplicationSubmission => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  // $FlowFixMe
  run_application_step_id: incr.next().value,
  submitted_date: moment().format(),
  review_status: casual.random_element(Object.keys(REVIEW_STATUS_TEXT_MAP)),
  review_status_date: moment().format(),
  submission_status: casual.random_element(
    Object.keys(SUBMISSION_STATUS_TEXT_MAP),
  ),
  interview_url: casual.url,
  take_interview_url: casual.url,
  interview_token: casual.uuid,
});

export const makeApplicationFacets = (): SubmissionFacetData => {
  const facets = {
    review_statuses: [
      REVIEW_STATUS_APPROVED,
      REVIEW_STATUS_REJECTED,
      REVIEW_STATUS_PENDING,
      REVIEW_STATUS_WAITLISTED,
    ].map((status) => ({
      review_status: status,
      count: casual.integer(1, 10),
    })),
    bootcamp_runs: [1, 2, 3].map((id) => ({
      id,
      title: casual.title,
      start_date: moment().format(),
      end_date: moment().format(),
      count: casual.integer(1, 10),
    })),
  };

  return facets;
};

export const setSubmissionToPending = (
  submission: ApplicationSubmission,
): ApplicationSubmission => {
  submission.review_status = REVIEW_STATUS_PENDING;
  submission.submitted_date = moment().format();
  submission.review_status_date = undefined;
  return submission;
};

export const setSubmissionToApproved = (
  submission: ApplicationSubmission,
): ApplicationSubmission => {
  submission.review_status = REVIEW_STATUS_APPROVED;
  submission.submitted_date = moment().format();
  submission.review_status_date = submission.submitted_date;
  return submission;
};

export const makeApplicationDetail = (): ApplicationDetail => {
  const run = generateFakeRun();
  // take off 10% to simulate a personal price
  const price =
    sum(run.installments.map((installment) => installment.amount)) * 0.9;
  return {
    // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
    id: incr.next().value,
    state: casual.random_element(Object.keys(APP_STATE_TEXT_MAP)),
    bootcamp_run: run,
    resume_url: casual.url,
    linkedin_url: casual.url,
    resume_upload_date: moment().format(),
    payment_deadline: moment().format(),
    is_paid_in_full: false,
    run_application_steps: [makeApplicationRunStep(), makeApplicationRunStep()],
    submissions: [],
    orders: [generateOrder()],
    created_on: moment().format(),
    price: price,
    user: makeUser(),
    enrollment: null,
  };
};

export const setToAwaitingResume = (
  appDetail: ApplicationDetail,
): ApplicationDetail => {
  appDetail.resume_upload_date = undefined;
  appDetail.resume_url = undefined;
  appDetail.linkedin_url = undefined;
  appDetail.submissions = [];
  return appDetail;
};

export const setToAwaitingSubmission = (
  appDetail: ApplicationDetail,
): ApplicationDetail => {
  appDetail = setToAwaitingResume(appDetail);
  appDetail.resume_upload_date = moment().format();
  appDetail.resume_url = casual.url;
  appDetail.submissions = [];
  return appDetail;
};

export const setToAwaitingReview = (
  appDetail: ApplicationDetail,
): ApplicationDetail => {
  appDetail = setToAwaitingSubmission(appDetail);
  let submission = makeApplicationSubmission();
  submission = setSubmissionToPending(submission);
  submission.run_application_step_id = appDetail.run_application_steps[0].id;
  appDetail.submissions = [submission];
  return appDetail;
};

export const setToAwaitingPayment = (
  appDetail: ApplicationDetail,
): ApplicationDetail => {
  appDetail = setToAwaitingSubmission(appDetail);
  appDetail.is_paid_in_full = false;
  for (let i = 0; i < appDetail.run_application_steps.length; i++) {
    let submission = makeApplicationSubmission();
    submission = setSubmissionToApproved(submission);
    submission.run_application_step_id = appDetail.run_application_steps[i].id;
    appDetail.submissions = appDetail.submissions.concat(submission);
  }
  return appDetail;
};

export const setToPaid = (appDetail: ApplicationDetail): ApplicationDetail => {
  appDetail = setToAwaitingPayment(appDetail);
  appDetail.is_paid_in_full = true;
  return appDetail;
};

export const makeSubmissionReview = (
  applicationId: number,
): SubmissionReview => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id: incr.next().value,
  review_status: casual.random_element(Object.keys(REVIEW_STATUS_TEXT_MAP)),
  learner: makeUser(),
  interview_url: casual.url,
  application_id: applicationId,
});
