// @flow
import React from "react"
import { useSelector } from "react-redux"
import { useRequest } from "redux-query-react"
import { useLocation } from "react-router"
import { Link } from "react-router-dom"
import { reverse } from "named-urls"

import SubmissionFacets from "../../components/SubmissionFacets"

import {
  submissionsQuery,
  submissionFacetsSelector
} from "../../lib/queries/submissions"
import { REVIEW_STATUS_DISPLAY_MAP } from "../../constants"
import { routes } from "../../lib/urls"
import type { SubmissionReview } from "../../flow/applicationTypes"
import qs from "query-string"

/* eslint-disable camelcase */
type RowProps = {
  submission: SubmissionReview
}
export function SubmissionRow({ submission }: RowProps) {
  const {
    review_status, // eslint-disable-line camelcase
    learner: { profile }
  } = submission

  const [label, className] = REVIEW_STATUS_DISPLAY_MAP[review_status]

  return (
    <div className="submission-row row my-3">
      <Link
        className="col-8 name"
        to={reverse(routes.review.detail, { submissionId: submission.id })}
      >
        {profile ? profile.name : ""}
      </Link>
      <Link
        className={`col-4 status ${className}`}
        to={reverse(routes.review.detail, { submissionId: submission.id })}
      >
        {label}
      </Link>
    </div>
  )
}
/* eslint-enable camelcase */

export default function ReviewDashboardPage() {
  const limit = 10
  const location = useLocation()
  const [{ isFinished }] = useRequest(submissionsQuery(location.search))
  const { count, results, facets } = useSelector(submissionFacetsSelector)
  const pages = count <= limit ? 1 : Math.ceil(count / limit)
  const {offset} = qs.parse(location.search) || 0

  return (
    <div className="review-dashboard-page container-lg">
      <div className="row">
        <div className="col-12">
          <h1>ADMISSION SYSTEM</h1>
        </div>
      </div>
      {isFinished && results ? (
        <div className="row mt-3">
          <div className="col-4">
            <SubmissionFacets facets={facets} />
          </div>
          <div className="container col-8">
            <div className="row">
              <div className="font-weight-bold text-uppercase col-8">
                Applicants
              </div>
              <div className="font-weight-bold text-uppercase col-4">
                Status
              </div>
            </div>
            {results.map((submission, i) => (
              <SubmissionRow key={i} submission={submission} />
            ))}
            <div className="row">
              { pages > 1 ? (
                <ul className="pagination">
                  {
                    [...Array(pages)].map((page, idx) => (
                        <li className={`page-item ${ offset === (limit*idx) ? "active" : ""}`}>
  
                        </li>
                      )
                    )
                  }
                </ul>
                ) : null
              }
          </div>
        </div>
      ) : null}
    </div>
  )
}
