// @flow
import { objOf } from "ramda"
import { nextState } from "./util"

import type { Application } from "../../flow/applicationTypes"

const applicationsKey = "applications"

export const applicationsSelector = (state: any): ?Array<Application> =>
  state.entities[applicationsKey]

export default {
  applicationsQuery: () => ({
    url:       "/api/applications/",
    transform: objOf(applicationsKey),
    update:    {
      [applicationsKey]: nextState
    }
  })
}
