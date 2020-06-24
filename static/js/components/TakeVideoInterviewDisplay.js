// @flow
import React, { useState } from "react"
import { useMutation } from "redux-query-react"

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
  stepId: number
}

export default function TakeVideoInterviewDisplay({
  application,
  stepId
}: Props) {
  const [hasError, setHasError] = useState(false)
  const [{ isPending }, createVideoInterview] = useMutation(() =>
    queries.applications.createVideoInterviewMutation(application.id, stepId)
  )

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
            setHasError(false)

            const result: HttpAuthResponse<VideoInterviewResponse> = await createVideoInterview()

            if (result.status === 200 && result.body.interview_link) {
              window.location = result.body.interview_link
              return
            }
            setHasError(true)
          }}
          disabled={isPending}
        >
          Take Interview at {JOBMA_SITE}
        </button>
      </div>

      {hasError ? (
        <div className="form-error">
          <p>
            We're unable to start a video interview for you at this time, please
            try again later. If you continue to see this message, please{" "}
            <a
              href="https://mitbootcamps.zendesk.com/hc/en-us/requests/new"
              target="_blank"
              rel="noopener noreferrer"
            >
              contact support
            </a>
            .
          </p>
        </div>
      ) : null}
    </div>
  )
}
