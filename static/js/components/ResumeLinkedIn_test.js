// @flow
import React from "react"
import { assert } from "chai"
import sinon from "sinon"
import { shallow } from "enzyme"
import { Field } from "formik"

import ResumeLinkedIn, {
  ResumeUploader,
  ResumeLinkedIn as InnerResumeLinkedIn
} from "./ResumeLinkedIn"
import { makeApplicationDetail } from "../factories/application"
import IntegrationTestHelper from "../util/integration_test_helper"
import { applicationDetailKey } from "../lib/queries/applications"

describe("ResumeLinkedIn", () => {
  const fakeResumeFilename = "my_resume.pdf",
    fakeResumeFilepath = `resumes/1/fd07666e-f546-4c86-8099-825628e68de8_${fakeResumeFilename}`
  let helper, renderPage, applicationDetail, resumeUrl

  beforeEach(() => {
    applicationDetail = makeApplicationDetail()
    applicationDetail.resume_filepath = fakeResumeFilepath
    resumeUrl = `/api/applications/${applicationDetail.id}/resume/`
    helper = new IntegrationTestHelper()
    renderPage = helper.configureHOCRenderer(
      ResumeLinkedIn,
      InnerResumeLinkedIn,
      {
        entities: {
          [applicationDetailKey]: {
            [applicationDetail.id]: applicationDetail
          }
        }
      },
      { applicationId: applicationDetail.id }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("has a title", async () => {
    const { inner } = await renderPage()
    assert.equal(inner.find("h1").text(), "Resume or LinkedIn Profile")
  })

  it("renders the uploader", async () => {
    const { inner } = await renderPage()
    const resumeUploader = inner.find(ResumeUploader)
    assert.isTrue(resumeUploader.exists())
    assert.deepEqual(resumeUploader.prop("application"), applicationDetail)
    assert.equal(resumeUploader.prop("resumeFilename"), fakeResumeFilename)
  })

  describe("resume uploader", () => {
    let onSuccessfulUploadStub

    beforeEach(() => {
      onSuccessfulUploadStub = helper.sandbox.stub()
    })

    it("renders no file name if a resume wasn't uploaded", async () => {
      const wrapper = shallow(
        <ResumeUploader
          application={applicationDetail}
          resumeFilename=""
          onSuccessfulUpload={onSuccessfulUploadStub}
        />
      )

      assert.isFalse(wrapper.find(".uploaded").exists())
    })

    it("renders a file name if a resume was uploaded", async () => {
      const wrapper = shallow(
        <ResumeUploader
          application={applicationDetail}
          resumeFilename={fakeResumeFilename}
          onSuccessfulUpload={onSuccessfulUploadStub}
        />
      )

      assert.equal(
        wrapper.find(".uploaded").html(),
        `<p class="uploaded">Your uploaded resume: <strong>${fakeResumeFilename}</strong></p>`
      )
    })
  })

  describe("LinkedIn form", () => {
    const renderFormik = async (...args) => {
      const { inner } = await renderPage(...args)
      const formik = inner.find("Formik")
      const rendered = shallow(formik.prop("render")({})).dive()
      return { formik, inner: rendered }
    }

    it("renders correctly", async () => {
      const { inner } = await renderFormik()

      assert.isTrue(inner.find("button[type='submit']").exists())
      assert.isTrue(
        inner
          .find(Field)
          .filter("[name='linkedInUrl']")
          .exists()
      )
    })

    it("submits linkedin url", async () => {
      const submitStub = helper.sandbox.stub()
      const fakeForm = document.createElement("form")
      fakeForm.setAttribute("class", "fake-form")
      // $FlowFixMe
      fakeForm.submit = submitStub

      const { formik } = await renderFormik()
      const linkedInUrl = "http://example.com"

      const setSubmittingStub = helper.sandbox.stub()
      const resetFormStub = helper.sandbox.stub()
      await formik.prop("onSubmit")(
        { linkedInUrl: linkedInUrl },
        { setSubmitting: setSubmittingStub, resetForm: resetFormStub }
      )
      sinon.assert.calledWith(
        helper.handleRequestStub.withArgs(resumeUrl),
        resumeUrl,
        "POST",
        {
          body: {
            linkedin_url: linkedInUrl
          },
          credentials: undefined,
          headers:     { "X-CSRFTOKEN": null }
        }
      )
      sinon.assert.calledOnce(resetFormStub)
    })
  })
})
