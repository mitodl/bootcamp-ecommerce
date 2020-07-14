// @flow
import { objOf, mergeDeepRight } from "ramda"

import { nextState } from "./util"

import { applicationsAPI, applicationDetailAPI, appResumeAPI } from "../urls"
import { DEFAULT_NON_GET_OPTIONS } from "../redux_query"
import type {
  Application,
  ApplicationDetail,
  ApplicationDetailState
} from "../../flow/applicationTypes"
// $FlowFixMe: This export exists
import type { QueryState } from "redux-query"

const applicationsKey = "applications"
export const applicationDetailKey = "applicationDetail"
export const createAppQueryKey = "createApplication"
export const appQueryKey = applicationsKey

export const applicationsSelector = (state: any): ?Array<Application> =>
  state.entities[applicationsKey]

export const allApplicationDetailSelector = (
  state: any
): { [string]: ApplicationDetail } => state.entities[applicationDetailKey]

// HACK: This wouldn't work with R.curry for some reason. Settling for a function that returns a function.
export const appDetailQuerySelector = (state: any) => (
  applicationId: string
): ?QueryState => state.queries[`appDetail.${applicationId}`]

export const applicationDetailSelector = (
  applicationId: number,
  state: any
): ApplicationDetail =>
  state.entities[applicationDetailKey][String(applicationId)]

export default {
  applicationsQuery: () => ({
    queryKey:  appQueryKey,
    url:       applicationsAPI.toString(),
    transform: objOf(applicationsKey),
    update:    {
      [applicationsKey]: nextState
    }
  }),
  createApplicationMutation: (bootcampRunId: number) => ({
    queryKey: createAppQueryKey,
    url:      applicationsAPI.toString(),
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
  applicationDetailQuery: (applicationId: string, force?: boolean) => ({
    queryKey:  `appDetail.${applicationId}`,
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
    },
    force: !!force
  }),
  applicationLinkedInUrlMutation: (
    applicationId: number,
    linkedinUrl: string
  ) => ({
    queryKey: "resume",
    url:      appResumeAPI.param({ applicationId }).toString(),
    body:     {
      linkedin_url: linkedinUrl
    },
    options:   DEFAULT_NON_GET_OPTIONS,
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
