// @flow
import { assert } from "chai"
import sinon from "sinon"
import { shallow } from "enzyme"

import UploadResumeView, {
  ResumeUploader,
  UploadResumeView as InnerUploadResumeView
} from "./UploadResumeView"

import { makeApplicationDetail } from "../factories/application"
import IntegrationTestHelper from "../util/integration_test_helper"
import { Field } from "formik/dist/index"

describe("UploadResumeView", () => {
  let helper, renderPage, application

  beforeEach(() => {
    application = makeApplicationDetail()
    helper = new IntegrationTestHelper()
    renderPage = helper.configureHOCRenderer(
      UploadResumeView,
      InnerUploadResumeView,
      {},
      { application: application }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders the drawer title, and other messages", async () => {
    const { inner } = await renderPage()
    assert.equal(
      inner.find(".drawer-title").text(),
      "Resume or LinkedIn Profile"
    )
  })

  it("renders no uploaded file name", async () => {
    application.resume_filepath = null
    const { inner } = await renderPage()

    assert.isFalse(inner.find(".uploaded-resume").exists())
  })

  it("renders the ResumeUploder", async () => {
    const { inner } = await renderPage()
    assert.ok(inner.find(ResumeUploader).exists())
  })

  describe("submitting linkedin url", () => {
    const renderFormik = async (...args) => {
      const { inner } = await renderPage(...args)
      const formik = inner.find("Formik")
      const rendered = shallow(formik.prop("render")({})).dive()
      return { formik, inner: rendered }
    }

    it("renders the linkedin url form", async () => {
      const { inner } = await renderFormik()

      assert.ok(inner.find("button[type='submit']").exists())
      assert.ok(
        inner
          .find(Field)
          .filter("[name='linkedinUrl']")
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
      const linkedinUrl = "http://example.com"

      const setSubmittingStub = helper.sandbox.stub()
      await formik.prop("onSubmit")(
        { linkedinUrl: linkedinUrl },
        { setSubmitting: setSubmittingStub }
      )
      sinon.assert.calledWith(
        helper.handleRequestStub.withArgs(
          `/api/applications/${application.id}/resume/`
        ),
        `/api/applications/${application.id}/resume/`,
        "POST",
        {
          body: {
            linkedin_url: linkedinUrl
          },
          credentials: undefined,
          headers:     { "X-CSRFTOKEN": null }
        }
      )
    })
  })
})
