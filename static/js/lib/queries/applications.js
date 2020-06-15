// @flow
import { objOf } from "ramda"

import { nextState } from "./util"
import { getCookie } from "../api"

import type {
  Application,
  ApplicationDetail,
  ApplicationDetailState,
  SubmissionReview,
  SubmissionReviewState,
  VideoInterviewResponse
} from "../../flow/applicationTypes"

const DEFAULT_NON_GET_OPTIONS = {
  headers: {
    "X-CSRFTOKEN": getCookie("csrftoken")
  }
}

const applicationsKey = "applications"
const applicationDetailKey = "applicationDetail"
export const createAppQueryKey = "createApplication"

const submissionDetailKey = "submissionReview"
const submissionsApiUrl = "/api/submissions/"

export const applicationsSelector = (state: any): ?Array<Application> =>
  state.entities[applicationsKey]

export const applicationDetailSelector = (
  state: any
): { [string]: ApplicationDetail } => state.entities[applicationDetailKey]

export const submissionDetailSelector = (
  state: any
): { [string]: SubmissionReview } => state.entities[submissionDetailKey]

export default {
  applicationsQuery: () => ({
    url:       "/api/applications/",
    transform: objOf(applicationsKey),
    update:    {
      [applicationsKey]: nextState
    }
  }),
  createApplicationMutation: (bootcampRunId: number) => ({
    queryKey: createAppQueryKey,
    url:      "/api/applications/",
    options:  {
      ...DEFAULT_NON_GET_OPTIONS,
      method: "POST"
    },
    body: {
      bootcamp_run_id: bootcampRunId
    },
    transform: objOf(applicationsKey),
    update:    {
      // If successful, add the newly-created application to the list of loaded applications
      [applicationsKey]: (
        prev: Array<Application>,
        newApplication: Application
      ) => [...(prev || []), newApplication]
    }
  }),
  applicationDetailQuery: (applicationId: string) => ({
    url:       `/api/applications/${applicationId}/`,
    transform: (json: ?ApplicationDetail) => {
      return {
        [applicationDetailKey]: {
          [applicationId]: json
        }
      }
    },
    update: {
      [applicationDetailKey]: (
        prev: ApplicationDetailState,
        transformed: ApplicationDetailState
      ) => ({
        ...prev,
        ...transformed
      })
    }
  }),
  submissionReviewQuery: (submissionId: number) => ({
    url:       `${submissionsApiUrl}${submissionId}/`,
    transform: (json: ?SubmissionReview) => {
      return {
        [submissionDetailKey]: {
          [submissionId]: json
        }
      }
    },
    update: {
      [submissionDetailKey]: (
        prev: SubmissionReviewState,
        transformed: SubmissionReviewState
      ) => ({
        ...prev,
        ...transformed
      })
    }
  }),
  submissionReviewMutation: (submission: SubmissionReview) => ({
    url:       `${submissionsApiUrl}${submission.id}/`,
    body:      submission,
    transform: (json: ?SubmissionReview) => {
      return {
        [submissionDetailKey]: {
          [submission.id]: json
        }
      }
    },
    update: {
      [submissionDetailKey]: (
        prev: SubmissionReviewState,
        transformed: SubmissionReviewState
      ) => ({
        ...prev,
        ...transformed
      })
    },
    options: {
      method:  "PATCH",
      headers: {
        "X-CSRFTOKEN": getCookie("csrftoken")
      }
    }
  }),
  createVideoInterviewQuery: (applicationId: string) => ({
    url:       `/api/applications/${applicationId}/video-interviews/`,
    transform: (json: ?VideoInterviewResponse) => ({
      bootcampRuns: json
    }),
    update: {
      bootcampRuns: (
        prev: VideoInterviewResponse,
        next: VideoInterviewResponse
      ) => next
    },
    options: {
      ...DEFAULT_NON_GET_OPTIONS,
      method: "POST"
    },
    force: true
  })
}
