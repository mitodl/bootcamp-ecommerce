// @flow
import React from "react"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"

import { DrawerCloseHeader } from "./Drawer"
import { JOBMA, JOBMA_SITE } from "../constants"
import queries from "../lib/queries"

import type {
  ApplicationDetail,
  VideoInterviewResponse
} from "../flow/applicationTypes"
import type { HttpAuthResponse } from "../flow/authTypes"

type Props = {
  application: ApplicationDetail,
  stepId: number,
  createVideoInterview: (
    applicationId: number,
    stepId: number
  ) => Promise<HttpAuthResponse<VideoInterviewResponse>>
}
export function TakeVideoInterviewDisplay({
  application,
  stepId,
  createVideoInterview
}: Props) {
  return (
    <div className="container drawer-wrapper take-video-interview">
      <DrawerCloseHeader />
      <h2 className="mb-5">Take Video Interview</h2>
      <p className="mb-5">
        Thank you for taking the video interview. To make your experience better
        we are collaborating with {JOBMA} and you will be taking this interview
        on their platform at {JOBMA_SITE}.
      </p>

      <div>
        <button
          className="btn-external-link"
          onClick={async () => {
            const {
              body: { interview_link: interviewLink }
            }: HttpAuthResponse<VideoInterviewResponse> = await createVideoInterview(
              application.id,
              stepId
            )
            if (interviewLink) {
              window.location = interviewLink
            }
          }}
        >
          Take Interview at {JOBMA_SITE}
        </button>
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
