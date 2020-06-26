// @flow
import { assert } from "chai"
import { times } from "ramda"
import { reverse } from "named-urls"

import ReviewDashboardPage from "./ReviewDashboardPage"

import IntegrationTestHelper from "../../util/integration_test_helper"
import { submissionsAPI } from "../../lib/urls"
import {
  makeApplicationFacets,
  makeSubmissionReview
} from "../../factories/application"
import { REVIEW_STATUS_DISPLAY_MAP } from "../../constants"
import { routes } from "../../lib/urls"

describe("ReviewDashboardPage", () => {
  let helper, render, facets, submissions

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    facets = makeApplicationFacets()
    submissions = times(makeSubmissionReview, 4)
    helper.handleRequestStub
      .withArgs(submissionsAPI.query({ limit: 1000 }).toString())
      .returns({
        status: 200,
        body:   {
          count:    submissions.length,
          next:     "next",
          previous: "previous",
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
})
