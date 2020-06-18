// @flow
import casual from "casual-browserify"
import sinon from "sinon"
import { assert } from "chai"

import TakeVideoInterviewDisplay from "./TakeVideoInterviewDisplay"

import IntegrationTestHelper from "../util/integration_test_helper"
import { makeApplicationDetail } from "../factories/application"

describe("TakeVideoInterviewDisplay", () => {
  let helper, renderPage, application, interviewLink, stepId
  beforeEach(() => {
    interviewLink = "http://fake.url/"
    stepId = casual.integer(0, 100)
    application = makeApplicationDetail()

    helper = new IntegrationTestHelper()
    renderPage = helper.configureReduxQueryRenderer(TakeVideoInterviewDisplay, {
      application,
      stepId
    })
    helper.handleRequestStub
      .withArgs(`/api/applications/${application.id}/video-interviews/`)
      .returns({
        status: 200,
        body:   {
          interview_link: interviewLink
        }
      })
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("takes the interview upon clicking the link", async () => {
    const { wrapper } = await renderPage()
    await wrapper.find(".take-video-interview a").prop("onClick")()
    sinon.assert.calledWith(
      helper.handleRequestStub,
      `/api/applications/${application.id}/video-interviews/`,
      "POST",
      {
        body: {
          step_id: stepId
        },
        credentials: undefined,
        headers:     {
          "X-CSRFTOKEN": null
        }
      }
    )
    assert.equal(window.location.toString(), interviewLink)
  })
})
