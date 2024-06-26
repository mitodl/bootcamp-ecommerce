// @flow
import {
  SUBMISSION_VIDEO,
  SUBMISSION_QUIZ,
  SUBMISSION_STATUS_PENDING,
  SUBMISSION_STATUS_SUBMITTED,
  REVIEW_STATUS_APPROVED,
  REVIEW_STATUS_REJECTED,
  REVIEW_STATUS_PENDING,
} from "../constants";

import type { BootcampRun, BootcampRunEnrollment } from "./bootcampTypes";
import type { User } from "./authTypes";
import type { HttpResponse } from "./httpTypes";

export type Application = {
  id: number,
  state: string,
  created_on: any,
  bootcamp_run: BootcampRun,
  certificate_link: string,
  enrollment: ?BootcampRunEnrollment,
  has_payments: boolean,
};

export type ValidAppStepType = SUBMISSION_VIDEO | SUBMISSION_QUIZ;

export type ApplicationRunStep = {
  id: number,
  due_date: string,
  step_order: number,
  submission_type: ValidAppStepType,
};

export type ValidReviewStatusType =
  | REVIEW_STATUS_APPROVED
  | REVIEW_STATUS_REJECTED
  | REVIEW_STATUS_PENDING;
export type ValidSubmissionStatusType =
  | SUBMISSION_STATUS_PENDING
  | SUBMISSION_STATUS_SUBMITTED;

export type ApplicationSubmission = {
  id: number,
  run_application_step_id: number,
  submitted_date: ?string,
  submission_status: ValidSubmissionStatusType,
  review_status: ValidReviewStatusType,
  review_status_date: ?string,
  interview_url: ?string,
  take_interview_url: ?string,
  interview_token: ?string,
};

export type LegacyOrderPartial = {
  id: number,
  status: string,
  created_on: string,
  updated_on: string,
};

export type ApplicationOrder = {
  total_price_paid: number,
  payment_method: string,
} & LegacyOrderPartial;

export type ResumeLinkedInDetail = {
  resume_url: ?string,
  linkedin_url: ?string,
  resume_upload_date: ?string,
};

export type ApplicationDetail = ResumeLinkedInDetail & {
  id: number,
  state: string,
  bootcamp_run: BootcampRun,
  payment_deadline: string,
  is_paid_in_full: boolean,
  run_application_steps: Array<ApplicationRunStep>,
  submissions: Array<ApplicationSubmission>,
  orders: Array<ApplicationOrder>,
  created_on: string,
  price: number,
  user: User,
  enrollment: ?BootcampRunEnrollment,
};

export type SubmissionReview = {
  id: number,
  learner: User,
  review_status: ?string,
  interview_url: ?string,
  application_id: number,
};

export type ApplicationDetailState = {
  [string]: ApplicationDetail,
};

export type SubmissionReviewState = {
  [string]: SubmissionReview,
};

type BootcampFacetOption = {
  id: number,
  title: string,
  start_date: string,
  end_date: string,
  count: number,
};

type ReviewStatusFacetOption = {
  review_status: string,
  count: number,
};

export type FacetOption = BootcampFacetOption | ReviewStatusFacetOption;

export type SubmissionFacetData = {
  bootcamp_runs: Array<BootcampFacetOption>,
  review_statuses: Array<ReviewStatusFacetOption>,
};

export type VideoInterviewResponse = {
  interview_link: string,
};

export type NewApplicationResponse = HttpResponse<Application>;
export type ResumeLinkedInResponse = HttpResponse<ResumeLinkedInDetail>;
export type ApplicationDetailResponse = HttpResponse<ApplicationDetail>;
