// @flow
import { objOf } from "ramda"
import { nextState } from "./util"

import type {
  Application,
  ApplicationDetail,
  ApplicationDetailState
} from "../../flow/applicationTypes"

const applicationsKey = "applications"
const applicationDetailKey = "applicationDetail"

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
