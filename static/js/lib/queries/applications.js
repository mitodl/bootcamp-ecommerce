// @flow
import { objOf, mergeDeepRight } from "ramda"

import { nextState } from "./util"
import { getCookie } from "../api"

import { DEFAULT_POST_OPTIONS } from "../redux_query"
import { applicationsAPI, applicationDetailAPI } from "../urls"

import type {
  Application,
  ApplicationDetail,
  ApplicationDetailState,
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

export const applicationsSelector = (state: any): ?Array<Application> =>
  state.entities[applicationsKey]

export const applicationDetailSelector = (
  state: any
): { [string]: ApplicationDetail } => state.entities[applicationDetailKey]

export default {
  applicationsQuery: () => ({
    url:       applicationsAPI.toString(),
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
    url:       applicationDetailAPI.param({ applicationId }).toString(),
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
  createVideoInterviewMutation: (applicationId: number, stepId: number) => ({
    url:  `/api/applications/${String(applicationId)}/video-interviews/`,
    body: {
      step_id: stepId
    },
    options: {
      ...DEFAULT_NON_GET_OPTIONS,
      method: "POST"
    },
    transform: (json: ?VideoInterviewResponse) => ({
      bootcampRuns: json
    }),
    update: {
      bootcampRuns: nextState
    },
    force: true
  }),
  applicationUploadResumeMutation: (
    linkedinUrl: string,
    applicationId: number
  ) => ({
    queryKey: "resume",
    url:      `/api/applications/${applicationId}/resume/`,
    body:     {
      linkedin_url: linkedinUrl
    },
    options: {
      ...DEFAULT_POST_OPTIONS
    },
    transform: (json: Object) => {
      return {
        [applicationDetailKey]: {
          [applicationId]: json
        }
      }
    },
    update: {
      [applicationDetailKey]: (
        prev: ApplicationDetailState,
        transformed: Object
      ) => mergeDeepRight(prev, transformed)
    }
  })
}
