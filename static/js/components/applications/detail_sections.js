// @flow
/* global SETTINGS: false */
import React from "react"
import * as R from "ramda"

import ProgressDetailRow from "./ProgressDetailRow"
import { formatReadableDateFromStr } from "../../util/util"
import { PAYMENT, PROFILE_VIEW, REVIEW_STATUS_REJECTED } from "../../constants"

import type { DrawerChangePayload } from "../../reducers/drawer"
import type {
  ApplicationDetail,
  ApplicationRunStep,
  ApplicationSubmission
} from "../../flow/applicationTypes"
import type { User } from "../../flow/authTypes"

type DetailSectionProps = {
  ready: boolean,
  fulfilled: boolean,
  openDrawer: (actionPayload: DrawerChangePayload) => void
}

type ProfileDetailProps = DetailSectionProps & {
  user: User
}

export const ProfileDetail = (props: ProfileDetailProps): React$Element<*> => {
  const { fulfilled, openDrawer, user } = props

  return (
    <ProgressDetailRow className="profile" fulfilled={fulfilled}>
      <h3>Profile Information</h3>
      <div className="col-12 col-sm-6 status-text">
        {user.profile && user.profile.updated_on ? (
          <div>
            <span className="label">Last Updated: </span>
            {formatReadableDateFromStr(user.profile.updated_on)}
          </div>
        ) : null}
      </div>
      <div className="col-12 col-sm-5 text-sm-right">
        <a
          className="btn-link"
          onClick={R.partial(openDrawer, [{ type: PROFILE_VIEW }])}
        >
          View/Edit Profile
        </a>
      </div>
    </ProgressDetailRow>
  )
}

type ResumeDetailProps = DetailSectionProps & {
  applicationDetail: ApplicationDetail
}

export const ResumeDetail = (props: ResumeDetailProps): React$Element<*> => {
  const { ready, fulfilled, applicationDetail } = props

  return (
    <ProgressDetailRow className="resume" fulfilled={fulfilled}>
      <h3>Resume or LinkedIn Profile</h3>
      <div className="col-12 col-sm-6 status-text">
        {applicationDetail.resume_upload_date && (
          <div>
            <span className="label">Completed: </span>
            {formatReadableDateFromStr(applicationDetail.resume_upload_date)}
          </div>
        )}
      </div>
      {ready && (
        <div className="col-12 col-sm-5 text-sm-right">
          <a className="btn-link">
            {fulfilled ?
              "View/Edit Resume or LinkedIn Profile" :
              "Add Resume or LinkedIn Profile"}
          </a>
        </div>
      )}
    </ProgressDetailRow>
  )
}

type SubmissionDetailProps = DetailSectionProps & {
  step: ApplicationRunStep,
  submission: ?ApplicationSubmission
}

export const VideoInterviewDetail = (
  props: SubmissionDetailProps
): React$Element<*> => {
  const { ready, fulfilled, step, submission } = props

  return (
    <ProgressDetailRow className="submission" fulfilled={fulfilled}>
      <h3>Video Interview</h3>
      <div className="col-12 col-sm-6 status-text">
        {submission && submission.submitted_date ? (
          <div>
            <span className="label">Completed: </span>
            {formatReadableDateFromStr(submission.submitted_date)}
          </div>
        ) : (
          <div>
            <span className="label">Deadline: </span>
            {formatReadableDateFromStr(step.due_date)}
          </div>
        )}
      </div>
      {ready && !fulfilled ? (
        <div className="col-12 col-sm-5 text-sm-right">
          <a className="btn-link">Take Video Interview</a>
        </div>
      ) : null}
    </ProgressDetailRow>
  )
}

export const QuizDetail = (props: SubmissionDetailProps): React$Element<*> => {
  const { fulfilled, step, submission } = props

  return (
    <ProgressDetailRow className="submission" fulfilled={fulfilled}>
      <h3>Quiz</h3>
      <div className="col-12 col-sm-6 status-text">
        {submission && submission.submitted_date ? (
          <div>
            <span className="label">Completed: </span>
            {formatReadableDateFromStr(submission.submitted_date)}
          </div>
        ) : (
          <div>
            <span className="label">Deadline: </span>
            {formatReadableDateFromStr(step.due_date)}
          </div>
        )}
      </div>
    </ProgressDetailRow>
  )
}

export const ReviewDetail = (
  props: SubmissionDetailProps
): React$Element<*> => {
  const { fulfilled, submission } = props

  let status
  if (submission) {
    if (!submission.review_status_date) {
      status = "Pending"
    } else if (submission.review_status === REVIEW_STATUS_REJECTED) {
      status = "Rejected"
    } else {
      status = "Approved"
    }
  }

  return (
    <ProgressDetailRow className="review" fulfilled={fulfilled}>
      <h3>Application Review</h3>
      {status && (
        <div className="col-12 col-sm-6 status-text">
          <span className="label">Status: </span>
          {status}
        </div>
      )}
    </ProgressDetailRow>
  )
}

type PaymentDetailProps = DetailSectionProps & {
  applicationDetail: ApplicationDetail
}

export const PaymentDetail = (props: PaymentDetailProps): React$Element<*> => {
  const { ready, fulfilled, openDrawer, applicationDetail } = props

  return (
    <ProgressDetailRow
      className="payment"
      fulfilled={applicationDetail.is_paid_in_full}
    >
      <h3>Payment</h3>
      <div className="col-12 col-sm-6 status-text">
        <span className="label">Deadline: </span>
        {formatReadableDateFromStr(applicationDetail.payment_deadline)}
      </div>
      {ready && !fulfilled ? (
        <div className="col-12 col-sm-5 text-sm-right">
          <a
            className="btn-link"
            onClick={R.partial(openDrawer, [
              {
                type: PAYMENT,
                meta: { application: applicationDetail }
              }
            ])}
          >
            Make a Payment
          </a>
        </div>
      ) : null}
    </ProgressDetailRow>
  )
}
