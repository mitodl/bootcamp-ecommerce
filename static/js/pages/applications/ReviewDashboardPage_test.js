// @flow
import { assert } from "chai"
import { times } from "ramda"
import { reverse } from "named-urls"
import casual from "casual-browserify"
import ReactPaginate from "react-paginate"

import ReviewDashboardPage from "./ReviewDashboardPage"

import IntegrationTestHelper from "../../util/integration_test_helper"
import { submissionsAPI } from "../../lib/urls"
import {
  makeApplicationFacets,
  makeSubmissionReview
} from "../../factories/application"
import { REVIEW_STATUS_DISPLAY_MAP } from "../../constants"
import { routes } from "../../lib/urls"
import { shouldIf } from "../../lib/test_utils"

describe("ReviewDashboardPage", () => {
  let helper, render, facets, submissions, applicationId

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    facets = makeApplicationFacets()
    applicationId = casual.integer(2, 30)
    submissions = times(() => makeSubmissionReview(applicationId), 10)
    helper.handleRequestStub
      .withArgs(submissionsAPI.query().toString())
      .returns({
        status: 200,
        body:   {
          count:    submissions.length,
          next:     "http://next.com?limit=10&offset=10",
          previous: null,
          facets,
          results:  submissions
        }
      })
    render = helper.configureReduxQueryRenderer(ReviewDashboardPage)
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("should render submissions, pass facets down", async () => {
    const { wrapper } = await render()
    const submissionRows = wrapper.find("SubmissionRow")
    submissions.forEach((submission, idx) => {
      assert.deepEqual(submission, submissionRows.at(idx).prop("submission"))
    })
    assert.deepEqual(wrapper.find("SubmissionFacets").prop("facets"), facets)
  })

  it("should show status, have link to submission detail page", async () => {
    const { wrapper } = await render()
    const row = wrapper.find("SubmissionRow").at(0)
    const [label, className] = REVIEW_STATUS_DISPLAY_MAP[
      submissions[0].review_status
    ]
    const statusDiv = row.find(".status").at(0)
    assert.equal(statusDiv.text(), label)
    assert.include(statusDiv.prop("className"), className)
    const link = row.find("Link").at(0)
    assert.equal(
      link.prop("to"),
      reverse(routes.review.detail, { submissionId: submissions[0].id })
    )
    assert.equal(link.text(), submissions[0].learner.profile.name)
  })

  //
  ;[
    [5, 12, 12, null, false],
    [15, 12, 12, null, true],
    [15, 12, null, 12, true],
    [15, 20, null, 20, false],
    [15, 10, null, null, true]
  ].forEach(([subCount, limit, nextOffset, previousOffset, showPaging]) => {
    it(`${shouldIf(
      showPaging
    )} render page controls if count is ${subCount} & limit is ${limit}`, async () => {
      helper.handleRequestStub
        .withArgs(submissionsAPI.query().toString())
        .returns({
          status: 200,
          body:   {
            count: subCount,
            next:  nextOffset ?
              `http://next.com?limit=${limit}&offset=${nextOffset}` :
              null,
            previous: previousOffset ?
              `http://previous.com?limit=${limit}&offset=${previousOffset}` :
              null,
            facets,
            results: submissions.slice(0, subCount)
          }
        })
      const { wrapper } = await render()
      const submissionPagination = wrapper.find("SubmissionPagination")
      assert.equal(
        submissionPagination.find(ReactPaginate).exists(),
        showPaging
      )
      assert.equal(submissionPagination.props().count, subCount)
      assert.equal(
        submissionPagination.props().limit,
        nextOffset || previousOffset || limit
      )
      assert.equal(submissionPagination.props().offset, 0)
    })
  })
})
