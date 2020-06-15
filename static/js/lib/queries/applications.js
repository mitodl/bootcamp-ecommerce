// @flow
import { objOf } from "ramda"

import { nextState } from "./util"
import { getCookie } from "../api"

import type {
  Application,
  ApplicationDetail,
  ApplicationDetailState
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
  })
}
