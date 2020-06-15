// @flow
import React from "react"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"

import queries from "../lib/queries"

import type { ApplicationDetail } from "../flow/applicationTypes"

type Props = {
  application: ApplicationDetail,
  createVideoInterview: (applicationId: number) => Promise<*>
}
export function TakeVideoInterviewDisplay({
  application,
  createVideoInterview
}: Props) {
  return (
    <div className="container take-video-interview auth-card">
      <h2>Take Video Interview</h2>
      <p>
        Thank you for taking the video interview. To make your experience better
        we are collaborating with Jobma and you will be taking this interview on
        their platform at jobma.com.
      </p>

      <div className="link">
        <a
          onClick={async () => {
            const {
              body: { interview_link: interviewLink }
            } = await createVideoInterview(application.id)
            if (interviewLink) {
              window.location = interviewLink
            }
          }}
        >
          Take Interview at videoplatform.com
        </a>
      </div>
    </div>
  )
}

const mapDispatchToProps = dispatch => ({
  createVideoInterview: (applicationId: string) =>
    dispatch(
      mutateAsync(queries.applications.createVideoInterviewQuery(applicationId))
    )
})

export default connect(null, mapDispatchToProps)(TakeVideoInterviewDisplay)
