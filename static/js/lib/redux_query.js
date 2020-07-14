// @flow
import { getCookie } from "./api"
import { isErrorStatusCode } from "../util/util"
// $FlowFixMe: This export exists
import type { QueryState } from "redux-query"

export const DEFAULT_NON_GET_OPTIONS = {
  headers: {
    "X-CSRFTOKEN": getCookie("csrftoken")
  }
}

// transforms a list of objects into a map of { id: object }
// for easy normalization and inclusion in the store
export const constructIdMap = (results: Array<Object>) => {
  const map = {}
  results.forEach(result => {
    map[result.id] = result
  })
  return map
}

export const getQueries = (state: Object) => state.queries
export const getEntities = (state: Object) => state.entities

export const isQueryInErrorState = (queryState?: QueryState) =>
  !!queryState && isErrorStatusCode(queryState.status)
