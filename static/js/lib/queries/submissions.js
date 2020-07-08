// @flow
import { createSelector } from "reselect"
import { compose, objOf, pick, merge, curry, propOr } from "ramda"
import qs from "query-string"

import { submissionsAPI, submissionDetailAPI } from "../urls"
import { getCookie } from "../api"

import type {
  SubmissionReview,
  SubmissionFacetData
} from "../../flow/applicationTypes"

const submissionsFacetsKey = "submissionsFacets"
const submissionKey = "submissions"

const submissionDetailTransform = curry((submissionId, json) => ({
  [submissionKey]: {
    [submissionId]: json
  }
}))

export const submissionQuery = (submissionId: number) => ({
  url:       submissionDetailAPI.param({ submissionId }).toString(),
  transform: submissionDetailTransform(submissionId),
  update:    {
    [submissionKey]: merge
  }
})

export const submissionsSelector = createSelector(
  state => state.entities,
  propOr({}, submissionKey)
)

type SubmissionReviewState = {
  [string]: SubmissionReview
}

export const submissionReviewMutation = (submission: SubmissionReview) => ({
  url:       submissionDetailAPI.param({ submissionId: submission.id }).toString(),
  body:      submission,
  transform: submissionDetailTransform(submission.id),
  update:    {
    [submissionKey]: (
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
})

const facetTransform = compose(
  objOf(submissionsFacetsKey),
  pick(["count", "next", "previous", "results", "facets"])
)

type FacetState = {
  count: number,
  next: string,
  previous: string,
  facets: SubmissionFacetData,
  results: Array<SubmissionReview>
}

export const submissionsQuery = (params: string) => {
  const url = submissionsAPI.query(qs.parse(params)).toString()

  return {
    queryKey:  params ? `submissions__${params}` : "submissions",
    url,
    transform: facetTransform,
    force:     true,
    update:    {
      [submissionsFacetsKey]: (
        prevState: { [string]: FacetState },
        nextState: FacetState
      ) => {
        const { count, next, previous, facets, results } = nextState

        // need to store the result of each request with different parameters
        // in order to deal with the situation where the user selects and then
        // unselects a given facet
        return {
          count,
          next,
          previous,
          facets,
          results
        }
      }
    }
  }
}

export const submissionFacetsSelector = createSelector(
  state => state.entities,
  entities => entities[submissionsFacetsKey] ?? {}
)
