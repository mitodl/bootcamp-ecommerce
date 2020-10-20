// @flow
import { assert } from "chai"
import qs from "query-string"

import IntegrationTestHelper from "../util/integration_test_helper"
import SubmissionFacets from "./SubmissionFacets"

import { makeApplicationFacets } from "../factories/application"
import {
  STATUS_FACET_KEY,
  BOOTCAMP_RUN_FACET_KEY,
  REVIEW_STATUS_DISPLAY_MAP
} from "../constants"
import { formatReadableDateFromStr } from "../util/util"

describe("SubmissionFacets", () => {
  let helper, facets, render

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    facets = makeApplicationFacets()
    render = helper.configureReduxQueryRenderer(SubmissionFacets, { facets })
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("should render all provided options", async () => {
    const { wrapper } = await render()

    const bootcampFacetOptions = wrapper
      .find(".facet")
      .at(0)
      .find("Option")
    facets.bootcamp_runs.forEach(({ title, startDate }, i) => {
      assert.equal(
        bootcampFacetOptions.at(i).prop("facetKey"),
        BOOTCAMP_RUN_FACET_KEY
      )
      assert.equal(
        bootcampFacetOptions.at(i).text(),
        `${title}: ${formatReadableDateFromStr(startDate)}`
      )
    })

    const reviewFacetOptions = wrapper
      .find(".facet")
      .at(1)
      .find("Option")
    // eslint-disable-next-line camelcase
    facets.review_statuses.forEach(({ review_status }, i) => {
      assert.equal(reviewFacetOptions.at(i).prop("facetKey"), STATUS_FACET_KEY)
      assert.equal(
        reviewFacetOptions.at(i).text(),
        REVIEW_STATUS_DISPLAY_MAP[review_status][0]
      )
    })
  })

  it("should bold options that are currently selected", async () => {
    const url = `/?${qs.stringify({
      review_status:   facets.review_statuses[0].review_status,
      bootcamp_run_id: facets.bootcamp_runs[0].id
    })}`
    helper.browserHistory.push(url)

    const { wrapper } = await render()

    wrapper.find("Option").forEach((option, i) => {
      if (i === 0 || i === 3) {
        assert.equal(
          "facet-option my-3 font-weight-bold",
          option.find("div").prop("className")
        )
      } else {
        assert.equal("facet-option my-3", option.find("div").prop("className"))
      }
    })
  })

  it("should let you activate a facet by clicking", async () => {
    const { wrapper } = await render()

    ;[0, 1].forEach(index => {
      wrapper
        .find(".facet")
        .at(index)
        .find("Option")
        .at(0)
        .simulate("click")
    })

    assert.equal(
      helper.currentLocation.search,
      "?bootcamp_run_id=1&review_status=approved"
    )
  })
})
