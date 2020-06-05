// @flow
import { createSelector } from "reselect"
import { propOr } from "ramda"
import qs from "query-string"

import { STATE_REGISTER_BACKEND_EMAIL } from "./auth"

export const qsSelector = createSelector(
  (_, ownProps) => ownProps.location.search,
  qs.parse
)

export const createParamSelector = (param: string, defaultValue?: any) => {
  return createSelector(qsSelector, propOr(defaultValue, param))
}

export const qsPartialTokenSelector = createParamSelector("partial_token")
export const qsVerificationCodeSelector = createParamSelector(
  "verification_code"
)
export const qsBackendSelector = createParamSelector(
  "backend",
  STATE_REGISTER_BACKEND_EMAIL
)
export const qsNextSelector = createParamSelector("next")
export const qsErrorSelector = createParamSelector("error")
export const qsEmailSelector = createParamSelector("email")

export const drawerSelector = createSelector(
  state => state.drawer,
  drawer => drawer
)
