// @flow
import React from "react"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"

import { JOBMA, JOBMA_SITE } from "../constants"
import queries from "../lib/queries"

import type { ApplicationDetail } from "../flow/applicationTypes"

type Props = {
  application: ApplicationDetail,
  stepId: number,
  createVideoInterview: (applicationId: number, stepId: number) => Promise<*>
}
export function TakeVideoInterviewDisplay({
  application,
  stepId,
  createVideoInterview
}: Props) {
  return (
    <div className="take-video-interview auth-card">
      <h2 className="text-uppercase">Take Video Interview</h2>
      <p>
        Thank you for taking the video interview. To make your experience better
        we are collaborating with {JOBMA} and you will be taking this interview
        on their platform at {JOBMA_SITE}.
      </p>

      <div className="link">
        <a
          onClick={async () => {
            const {
              body: { interview_link: interviewLink }
            } = await createVideoInterview(application.id, stepId)
            if (interviewLink) {
              window.location = interviewLink
            }
          }}
        >
          Take Interview at {JOBMA_SITE}
        </a>
      </div>
    </div>
  )
}

const mapDispatchToProps = dispatch => ({
  createVideoInterview: (applicationId: number, stepId: number) =>
    dispatch(
      mutateAsync(
        queries.applications.createVideoInterviewMutation(applicationId, stepId)
      )
    )
})

export default connect(null, mapDispatchToProps)(TakeVideoInterviewDisplay)
