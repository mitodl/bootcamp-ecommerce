// @flow
import React from "react"

import { JOBMA, JOBMA_SITE } from "../constants"

import type { ApplicationDetail } from "../flow/applicationTypes"

type Props = {
  application: ApplicationDetail,
  stepId: number
}

export default function TakeVideoInterviewDisplay({
  application,
  stepId
}: Props) {
  const submission = application.submissions.find(
    submission => submission.run_application_step_id === stepId
  )
  const url = submission && submission.take_interview_url
  const token = submission && submission.interview_token

  return (
    <div className="container drawer-wrapper take-video-interview">
      <h2 className="mb-5">Take Video Interview</h2>
      <p className="mb-5">
        Thank you for taking the video interview. To make your experience better
        we are collaborating with {JOBMA} and you will be taking this interview
        on their platform at {JOBMA_SITE}.
      </p>

      {token ? <p className="mb-5">If you are on mobile, please enter this token when asked: {token}</p> : null}

      <div>
        <a
          className="btn-external-link btn-styled"
          href={url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Take Interview at {JOBMA_SITE}
        </a>
      </div>
    </div>
  )
}
