// @flow
import React from "react"
import { useSelector } from "react-redux"
import { useRequest } from "redux-query-react"
import { useHistory, useLocation } from "react-router"
import { Link } from "react-router-dom"
import ReactPaginate from "react-paginate"
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
import urljoin from "url-join"

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

type PaginateProps = {
  limit: number,
  count: number,
  offset: number
}

export function SubmissionPagination(props: PaginateProps) {
  const { limit, count, offset } = props

  const initialPage = offset ? offset / limit : 0
  const pageCount = count <= limit ? 1 : Math.ceil(count / limit)
  const history = useHistory()

  const handlePageClick = data => {
    const selected = data.selected
    const newOffset = Math.ceil(selected * limit)
    if (newOffset !== offset) {
      const updatedParams = {
        ...qs.parse(location.search),
        offset: newOffset,
        limit:  limit
      }
      const url = urljoin(location.pathname, `/?${qs.stringify(updatedParams)}`)
      history.push(url)
    }
  }

  return pageCount > 1 ? (
    <div className="submission-paging row justify-content-center">
      <ReactPaginate
        previousLabel={"previous"}
        nextLabel={"next"}
        pageCount={pageCount}
        marginPagesDisplayed={2}
        initialPage={initialPage}
        pageRangeDisplayed={5}
        onPageChange={handlePageClick}
        containerClassName={"pagination"}
        subContainerClassName={"pages pagination"}
        activeClassName={"active"}
        breakClassName="page-item"
        breakLabel={<div className="page-link">...</div>}
        pageClassName="page-item"
        previousClassName="page-item"
        nextClassName="page-item"
        pageLinkClassName="page-link"
        previousLinkClassName="page-link"
        nextLinkClassName="page-link"
      />
    </div>
  ) : null
}
/* eslint-enable camelcase */

export default function ReviewDashboardPage() {
  const location = useLocation()
  const [{ isFinished }] = useRequest(submissionsQuery(location.search))
  const { next, previous, count, results, facets } = useSelector(
    submissionFacetsSelector
  )

  const offset = qs.parse(location.search).offset || 0
  const limit = next ?
    qs.parse(new URL(next).search).limit :
    previous ?
      qs.parse(new URL(previous).search).limit :
      10

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
            <SubmissionPagination limit={limit} count={count} offset={offset} />
          </div>
        </div>
      ) : null}
    </div>
  )
}
