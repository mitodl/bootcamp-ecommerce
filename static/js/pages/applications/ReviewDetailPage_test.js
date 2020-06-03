/* global SETTINGS: false */
import { assert } from "chai"
import sinon from "sinon"

import IntegrationTestHelper from "../../util/integration_test_helper"
import { makeUser } from "../../factories/user"
import {
  makeApplicationDetail,
  makeSubmissionReview
} from "../../factories/application"
import {
  REVIEW_STATUS_APPROVED,
  REVIEW_STATUS_PENDING,
  REVIEW_STATUS_REJECTED
} from "../../constants"
import ReviewDetailPage from "./ReviewDetailPage"

import { shouldIf } from "../../lib/test_utils"
import { getFilenameFromPath, isNilOrBlank } from "../../util/util"
import wait from "waait"

describe("ReviewDetailPage", () => {
  let helper,
    fakeUser,
    renderPage,
    fakeApplication,
    fakeApplicationDetail,
    fakeApplicationSubmission,
    fakeSubmissionReview

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    fakeSubmissionReview = makeSubmissionReview()
    fakeSubmissionReview.review_status = REVIEW_STATUS_PENDING
    fakeApplication = fakeSubmissionReview.bootcamp_application
    fakeUser = fakeSubmissionReview.learner
    fakeApplicationSubmission = {
      id:                      fakeSubmissionReview.id,
      run_application_step_id: fakeSubmissionReview.run_application_step_id,
      submitted_date:          fakeSubmissionReview.submitted_date,
      review_status:           fakeSubmissionReview.review_status,
      review_status_date:      fakeSubmissionReview.review_status_date
    }
    fakeApplicationDetail = makeApplicationDetail()
    fakeApplicationDetail.id = fakeApplication.id
    fakeApplicationDetail.bootcamp_run_id = fakeApplication.bootcamp_run_id
    fakeApplicationDetail.submissions = [fakeApplicationSubmission]

    helper.handleRequestStub
      .withArgs(
        `/api/applications/${fakeSubmissionReview.bootcamp_application.id}/`
      )
      .returns({
        status: 200,
        body:   fakeApplicationDetail
      })

    helper.handleRequestStub
      .withArgs(`/api/submissions/${fakeSubmissionReview.id}/`)
      .returns({
        status: 200,
        body:   fakeSubmissionReview
      })

    renderPage = helper.configureReduxQueryRenderer(
      ReviewDetailPage,
      {
        match: {
          params: {
            submissionId: fakeSubmissionReview.id
          }
        }
      },
      {
        entities: {
          currentUser: makeUser()
        }
      }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders the user's details", async () => {
    const { wrapper } = await renderPage()
    assert.isTrue(wrapper.find("UserDetails").exists())
  })

  //
  ;["http://resume.jpg", null].forEach(resumeFile => {
    it(`${shouldIf(
      !!resumeFile
    )} render the resume section if resume_file is ${String(
      resumeFile
    )}`, async () => {
      fakeApplicationDetail.resume_filepath = resumeFile
      const { wrapper } = await renderPage()
      const resumeDiv = wrapper.find(".resume")
      assert.equal(resumeDiv.exists(), !isNilOrBlank(resumeFile))
      if (!isNilOrBlank(resumeFile)) {
        assert.equal(
          resumeDiv.find("a").prop("href"),
          fakeApplicationDetail.resume_filepath
        )
        assert.equal(
          resumeDiv.find("a").text(),
          getFilenameFromPath(fakeApplicationDetail.resume_filepath)
        )
      }
    })
  })

  //
  ;["http://linkedin/user", null].forEach(linkedinUrl => {
    it(`${shouldIf(
      !isNilOrBlank(linkedinUrl)
    )} render the LinkedIn section if LinkedIn URL is ${String(
      linkedinUrl
    )}`, async () => {
      fakeApplicationDetail.linkedin_url = linkedinUrl
      const { wrapper } = await renderPage()
      const linkedinDiv = wrapper.find(".linkedin")
      assert.equal(linkedinDiv.exists(), !isNilOrBlank(linkedinUrl))
      if (!isNilOrBlank(linkedinUrl)) {
        assert.equal(
          linkedinDiv.find("a").prop("href"),
          fakeApplicationDetail.linkedin_url
        )
        assert.equal(linkedinDiv.find("a").text(), fakeUser.profile.name)
      }
    })
  })

  //
  ;["http://linkedin/user", null].forEach(interviewUrl => {
    it(`${shouldIf(
      !isNilOrBlank(interviewUrl)
    )} render the LinkedIn section if LinkedIn URL is ${String(
      interviewUrl
    )}`, async () => {
      fakeSubmissionReview.interview_url = interviewUrl
      const { wrapper } = await renderPage()
      const interviewDiv = wrapper.find(".interview")
      assert.equal(interviewDiv.exists(), !isNilOrBlank(interviewUrl))
      if (!isNilOrBlank(interviewUrl)) {
        assert.equal(
          interviewDiv.find("a").prop("href"),
          fakeSubmissionReview.interview_url
        )
        assert.equal(
          interviewDiv.find("a").text(),
          `Interview for ${fakeUser.profile.name}`
        )
      }
    })
  })

  //
  ;[
    [0, REVIEW_STATUS_APPROVED],
    [1, REVIEW_STATUS_REJECTED]
  ].forEach(([position, status]) => {
    it(`should display a success alert after status is set to ${status}`, async () => {
      const { wrapper } = await renderPage()
      const body = { ...fakeSubmissionReview, review_status: status }
      helper.handleRequestStub
        .withArgs(`/api/submissions/${fakeSubmissionReview.id}/`)
        .returns({
          status: 200,
          body
        })

      const event = {
        target: {
          name:  "status",
          value: status
        }
      }

      wrapper
        .find(".radio-status")
        .at(position)
        .find("input")
        .simulate("change", event)
      wrapper.update()
      wrapper.find(".btn-submit").simulate("click")
      await wait()
      wrapper.update()

      sinon.assert.calledWith(
        helper.handleRequestStub,
        `/api/submissions/${fakeSubmissionReview.id}/`,
        "PATCH",
        { body, credentials: undefined, headers: { "X-CSRFTOKEN": "" } }
      )
      assert.equal(wrapper.find("Alert").text(), `Submission ${status}`)
    })
  })

  it("should display an alert if anything goes wrong on submit", async () => {
    const { wrapper } = await renderPage()
    const errorMsg = "An error occurred"

    helper.handleRequestStub
      .withArgs(`/api/submissions/${fakeSubmissionReview.id}/`)
      .returns({
        status: 403,
        body:   { detail: errorMsg }
      })

    wrapper
      .find(".radio-status")
      .at(0)
      .find("input")
      .simulate("change", { target: { value: "approved" } })
    wrapper.update()
    wrapper.find(".btn-submit").simulate("click")
    await wait()
    wrapper.update()
    assert.equal(wrapper.find("Alert").text(), errorMsg)
  })
})
