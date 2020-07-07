// @flow
/* global SETTINGS: false */
import React, { useState, useEffect } from "react"
import { useSelector } from "react-redux"
import { useRequest, useMutation } from "redux-query-react"
import { MetaTags } from "react-meta-tags"

import queries from "../../lib/queries"
import { allApplicationDetailSelector } from "../../lib/queries/applications"
import {
  submissionQuery,
  submissionReviewMutation,
  submissionsSelector
} from "../../lib/queries/submissions"
import { formatTitle, getFilenameFromPath, isNilOrBlank } from "../../util/util"

import {
  REVIEW_DETAIL_TITLE,
  REVIEW_STATUS_APPROVED,
  REVIEW_STATUS_PENDING,
  REVIEW_STATUS_REJECTED,
  REVIEW_STATUS_WAITLISTED
} from "../../constants"
import UserDetails from "../../components/UserDetails"

import { Alert } from "reactstrap"

import type { Match } from "react-router"
import type {
  ApplicationDetail,
  SubmissionReview
} from "../../flow/applicationTypes"
import type { User } from "../../flow/authTypes"

type PageProps = {
  match: Match
}

type FormProps = {
  submission: SubmissionReview
}

type DetailProps = {
  submission: SubmissionReview,
  application: ApplicationDetail,
  user: User
}

const ReviewPanelRight = (props: FormProps) => {
  const { submission } = props

  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)
  const [selection, setSelection] = useState("")

  const clearState = () => {
    setSelection(submission.review_status || "")
    setError()
  }

  useEffect(() => {
    clearState()
  }, [submission])

  const [{ isPending }, updateStatus] = useMutation(status =>
    // $FlowFixMe
    submissionReviewMutation({
      ...submission,
      review_status: status
    })
  )

  const onSubmit = async (status: string) => {
    if (isNilOrBlank(status)) {
      return
    }
    const result = await updateStatus(status)
    if (result.status === 200) {
      setSuccess(true)
      setError()
    } else {
      setError(result.body.detail)
      setSuccess(false)
    }
  }

  const onUpdate = async (e: Object) => {
    await setSelection(e.target.value)
  }

  const currentSelection = selection || submission.review_status

  return (
    <div className="col-3 review-card review-panel-right">
      <div className="status">
        <h3>STATUS</h3>
        <div className="form-check radio-status">
          <input
            className="form-check-input"
            id="submission_approve"
            type="radio"
            name="submission_status"
            value={REVIEW_STATUS_APPROVED}
            checked={currentSelection === REVIEW_STATUS_APPROVED}
            onChange={onUpdate}
          />
          <label className="form-check-label" htmlFor="submission_approve">
            Approve
          </label>
        </div>
        <div className="form-check radio-status">
          <input
            className="form-check-input"
            id="submission_reject"
            type="radio"
            name="submission_status"
            value={REVIEW_STATUS_REJECTED}
            checked={currentSelection === REVIEW_STATUS_REJECTED}
            onChange={onUpdate}
          />
          <label className="form-check-label" htmlFor="submission_reject">
            Reject
          </label>
        </div>
        <div className="form-check radio-status">
          <input
            className="form-check-input"
            id="submission_waitlist"
            type="radio"
            name="submission_status"
            value={REVIEW_STATUS_WAITLISTED}
            checked={currentSelection === REVIEW_STATUS_WAITLISTED}
            onChange={onUpdate}
          />
          <label className="form-check-label" htmlFor="submission_waitlist">
            Waitlist
          </label>
        </div>
        <div className="form-check radio-status">
          <input
            className="form-check-input"
            id="submission_reject"
            type="radio"
            name="submission_status"
            disabled={submission.review_status !== REVIEW_STATUS_PENDING}
            value={REVIEW_STATUS_PENDING}
            checked={currentSelection === REVIEW_STATUS_PENDING}
            onChange={onUpdate}
          />
          <label className="form-check-label" htmlFor="submission_pending">
            Not Reviewed
          </label>
        </div>
        <div className="radio-status bottom-divider">
          <button
            type="submit"
            disabled={isPending || !selection}
            onClick={() => {
              onSubmit(selection)
            }}
            className="btn btn-danger btn-submit"
          >
            OK
          </button>
        </div>
      </div>
      {!isNilOrBlank(error) ? (
        <Alert color="danger" onClick={() => setError(null)}>
          {error}
        </Alert>
      ) : null}
      {success ? (
        <Alert color="success" onClick={() => setSuccess(false)}>
          {// $FlowFixMe: review_status won't be null here
            `Submission ${submission.review_status}`}
        </Alert>
      ) : null}
    </div>
  )
}

const ReviewPanelLeft = (props: DetailProps) => {
  const { submission, application, user } = props
  const userDisplayName = user.profile ? user.profile.name : user.username
  return (
    <div className="col-8 review-card review-panel-left">
      <div className="row section">
        <h3>{userDisplayName}</h3>
      </div>
      {submission.interview_url ? (
        <div className="row section interview">
          <div className="col">
            <div className="row">
              <h3>Video Interview</h3>
            </div>
            <div className="row">
              <a
                href={submission.interview_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Interview for {userDisplayName}
              </a>
            </div>
          </div>
        </div>
      ) : null}
      <div className="row section">
        <UserDetails user={user} />
      </div>
      {application.resume_url ? (
        <div className="row section resume">
          <div className="col">
            <div className="row">
              <h3>Resume</h3>
            </div>
            <div className="row">
              <a
                href={application.resume_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {getFilenameFromPath(application.resume_url)}
              </a>
              <embed
                type="application/pdf"
                src={application.resume_url}
                width="100%"
                height="375"
              />
            </div>
          </div>
        </div>
      ) : null}
      {application.linkedin_url ? (
        <div className="row section linkedin">
          <div className="col">
            <div className="row">
              <h3>LinkedIn Profile</h3>
            </div>
            <div className="row">
              <a
                href={application.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {userDisplayName}
              </a>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default function ReviewDetailPage(props: PageProps) {
  const { match } = props
  const { submissionId } = match.params

  useRequest(submissionQuery(submissionId))
  const submissions = useSelector(submissionsSelector)
  const submission = submissions ? submissions[submissionId] : null

  useRequest(
    submission ?
      queries.applications.applicationDetailQuery(submission.application_id) :
      null
  )

  const applicationDetails = useSelector(allApplicationDetailSelector)
  const application =
    applicationDetails && submission ?
      applicationDetails[submission.application_id] :
      null
  const user = submission ? submission.learner : null

  if (!submission || !application || !user) {
    return null
  }

  return (
    <div className="container applications-page">
      <MetaTags>
        <title>{formatTitle(REVIEW_DETAIL_TITLE)}</title>
      </MetaTags>
      <div className="row">
        <h1 className="col-12">{REVIEW_DETAIL_TITLE}</h1>
      </div>
      <div className="row">
        <ReviewPanelLeft
          submission={submission}
          application={application}
          user={user}
        />
        <ReviewPanelRight submission={submission} />
      </div>
    </div>
  )
}
