/* global SETTINGS: false */
import { assert } from "chai"
import sinon from "sinon"
import React from "react"
import { shallow } from "enzyme"
import wait from "waait"

import ApplicationDashboardPage, {
  ApplicationDashboardPage as InnerAppDashboardPage
} from "./ApplicationDashboardPage"
import IntegrationTestHelper from "../../util/integration_test_helper"
import {
  APP_STATE_TEXT_MAP,
  NEW_APPLICATION,
  SUBMISSION_QUIZ,
  SUBMISSION_STATUS_PENDING,
  SUBMISSION_STATUS_SUBMITTED,
  SUBMISSION_VIDEO
} from "../../constants"
import {
  makeApplication,
  makeApplicationDetail,
  makeApplicationRunStep,
  setToAwaitingPayment,
  setToAwaitingResume,
  setToAwaitingReview,
  setToAwaitingSubmission,
  setToPaid
} from "../../factories/application"
import {
  makeCompleteUser,
  makeIncompleteUser,
  makeUser
} from "../../factories/user"
import { shouldIf } from "../../lib/test_utils"

import type {
  Application,
  ApplicationDetail
} from "../../flow/applicationTypes"

describe("ApplicationDashboardPage", () => {
  let helper,
    fakeUser,
    renderPage,
    fakeApplicationDetail,
    fakeApplications = []

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    fakeUser = makeUser()
    fakeApplications = [makeApplication(), makeApplication()]
    fakeApplicationDetail = makeApplicationDetail()
    fakeApplicationDetail.id = fakeApplications[0].id

    helper.handleRequestStub.withArgs("/api/applications/").returns({
      status: 200,
      body:   fakeApplications
    })

    helper.handleRequestStub
      .withArgs(`/api/applications/${String(fakeApplicationDetail.id)}/`)
      .returns({
        status: 200,
        body:   fakeApplicationDetail
      })

    renderPage = helper.configureReduxQueryRenderer(
      ApplicationDashboardPage,
      {},
      {
        entities: {
          currentUser: fakeUser
        }
      }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders the user's name", async () => {
    const { wrapper } = await renderPage()
    assert.equal(wrapper.find("h2.name").text(), fakeUser.profile.name)
  })

  it("renders a card for each application that a user has", async () => {
    fakeApplications[0].state = "AWAITING_PROFILE_COMPLETION"
    fakeApplications[1].state = "AWAITING_SUBMISSION_REVIEW"
    const { wrapper } = await renderPage()
    const cards = wrapper.find(".application-card")
    assert.lengthOf(cards, fakeApplications.length)
    for (let i = 0; i < cards.length; i++) {
      assert.equal(
        cards
          .at(i)
          .find("h2")
          .text(),
        fakeApplications[i].bootcamp_run.bootcamp.title
      )
      assert.equal(
        cards
          .at(i)
          .find(".status-col")
          .text(),
        `Application Status: ${APP_STATE_TEXT_MAP[fakeApplications[i].state]}`
      )
    }
  })

  it("renders a thumbnail for an applied bootcamp if one exists", async () => {
    fakeApplications[0].bootcamp_run.page.thumbnail_image_src = null
    fakeApplications[1].bootcamp_run.page.thumbnail_image_src =
      "http://example.com/img.jpg"
    const { wrapper } = await renderPage()
    const cards = wrapper.find(".application-card")
    assert.isFalse(
      cards
        .at(0)
        .find("img")
        .exists()
    )
    assert.isTrue(
      cards
        .at(1)
        .find("img")
        .exists()
    )
  })

  it("shows a button to open the new application drawer", async () => {
    const openDrawerStub = sinon.spy()
    const { wrapper, store } = await renderPage({ openDrawer: openDrawerStub })

    const newAppButton = wrapper.find("button.new-application-btn")
    await newAppButton.simulate("click")
    await wait()

    const appliedRunIds = fakeApplications.map(
      (application: Application) => application.bootcamp_run.id
    )
    assert.deepEqual(store.getState().drawer, {
      drawerState: NEW_APPLICATION,
      drawerOpen:  true,
      drawerMeta:  { appliedRunIds: appliedRunIds }
    })
  })

  it("loads detailed application data when the detail section is expanded", async () => {
    const applicationIndex = 0
    const { wrapper } = await renderPage()
    let firstApplicationCard = wrapper
      .find(".application-card")
      .at(applicationIndex)
    assert.isFalse(firstApplicationCard.find("Collapse").prop("isOpen"))
    const expandLink = firstApplicationCard.find(".expand-collapse")
    assert.include(expandLink.text(), "Expand")
    assert.isFalse(firstApplicationCard.find(".application-detail").exists())

    await expandLink.simulate("click")
    await wait()
    wrapper.update()
    firstApplicationCard = wrapper
      .find(".application-card")
      .at(applicationIndex)
    sinon.assert.calledWith(
      helper.handleRequestStub,
      `/api/applications/${String(fakeApplicationDetail.id)}/`,
      "GET"
    )
    assert.isTrue(firstApplicationCard.find("Collapse").prop("isOpen"))
    assert.include(
      firstApplicationCard
        .find(".btn-text")
        .last()
        .text(),
      "Collapse"
    )
    assert.isTrue(firstApplicationCard.find(".application-detail").exists())
  })

  describe("detail view", () => {
    let defaultProps,
      application: Application,
      applicationDetail: ApplicationDetail,
      renderExpanded: Function,
      openDrawerStub

    beforeEach(() => {
      openDrawerStub = sinon.stub()
      application = makeApplication()
      applicationDetail = makeApplicationDetail()
      applicationDetail.id = application.id
      applicationDetail.run_application_steps = [
        makeApplicationRunStep(SUBMISSION_VIDEO),
        makeApplicationRunStep(SUBMISSION_QUIZ)
      ]
      applicationDetail.submissions = []
      defaultProps = {
        applications:         [application],
        allApplicationDetail: { [application.id]: applicationDetail },
        currentUser:          makeCompleteUser(),
        fetchAppDetail:       sinon.stub(),
        openDrawer:           openDrawerStub
      }
      // This function renders the component then sets the state so the detail section is expanded
      renderExpanded = async props => {
        const wrapper = await shallow(<InnerAppDashboardPage {...props} />)
        wrapper.setState({
          collapseVisible: { [application.id]: true }
        })
        wrapper.update()
        return wrapper
      }
    })

    //
    ;[
      [false, "for user with incomplete profile"],
      [true, "for user with complete profile"]
    ].forEach(([isComplete, desc]) => {
      it(`shows profile details ${desc}`, async () => {
        const user = isComplete ? makeCompleteUser() : makeIncompleteUser()
        const wrapper = await renderExpanded({
          ...defaultProps,
          currentUser: user
        })

        const profileDetail = wrapper.find("ProfileDetail")
        assert.isTrue(profileDetail.exists())
        assert.deepEqual(profileDetail.props(), {
          ready:      true,
          fulfilled:  isComplete,
          openDrawer: openDrawerStub,
          user:       user
        })
      })
    })

    //
    ;[
      [false, false, "incomplete profile"],
      [true, false, "complete profile"],
      [true, true, "submitted resume"]
    ].forEach(([hasProfile, hasResume, desc]) => {
      it(`shows resume details with ${desc}`, async () => {
        let newApplicationDetail = Object.assign({}, applicationDetail)
        newApplicationDetail =
          hasProfile && hasResume ?
            setToAwaitingSubmission(newApplicationDetail) :
            setToAwaitingResume(newApplicationDetail)
        const props = {
          ...defaultProps,
          allApplicationDetail: {
            [application.id]: newApplicationDetail
          },
          currentUser: hasProfile ? makeCompleteUser() : makeIncompleteUser()
        }
        const wrapper = await renderExpanded(props)

        const resumeDetail = wrapper.find("ResumeDetail")
        assert.isTrue(resumeDetail.exists())
        assert.deepEqual(resumeDetail.props(), {
          ready:             hasProfile,
          fulfilled:         hasResume,
          openDrawer:        openDrawerStub,
          applicationDetail: newApplicationDetail
        })
      })
    })

    //
    ;[
      //[false, false, false, false, "before the resume has been submitted"],
      //[true, false, false, false, "before the user submits it"],
      //[true, true, false, false, "clicked take interview link"],
      //[true, true, true, false, "finished interview, awaiting review"],
      [true, true, true, true, "after approval"]
    ].forEach(([hasResume, hasSubmission, hasSubmitted, isApproved, desc]) => {
      it(`shows details about a video submission ${desc}`, async () => {
        let newApplicationDetail = Object.assign({}, applicationDetail)
        if (!hasResume) {
          newApplicationDetail = setToAwaitingResume(newApplicationDetail)
        } else if (!hasSubmission) {
          newApplicationDetail = setToAwaitingSubmission(newApplicationDetail)
        } else {
          newApplicationDetail = isApproved ?
            setToAwaitingPayment(newApplicationDetail) :
            setToAwaitingReview(newApplicationDetail)
          newApplicationDetail.submissions.forEach(submission => {
            submission.submission_status = hasSubmitted ?
              SUBMISSION_STATUS_SUBMITTED :
              SUBMISSION_STATUS_PENDING
          })
        }
        const props = {
          ...defaultProps,
          allApplicationDetail: {
            [application.id]: newApplicationDetail
          }
        }
        const wrapper = await renderExpanded(props)

        const videoInterviewDetail = wrapper.find("VideoInterviewDetail")
        assert.isTrue(videoInterviewDetail.exists())
        const reviewDetail = wrapper.find("ReviewDetail")
        assert.isTrue(reviewDetail.exists())
        assert.deepEqual(videoInterviewDetail.props(), {
          ready:             hasResume,
          fulfilled:         hasSubmission,
          openDrawer:        openDrawerStub,
          step:              newApplicationDetail.run_application_steps[0],
          submission:        newApplicationDetail.submissions[0],
          applicationDetail: newApplicationDetail
        })
        assert.deepEqual(reviewDetail.first().props(), {
          ready:             true,
          fulfilled:         isApproved,
          openDrawer:        openDrawerStub,
          step:              newApplicationDetail.run_application_steps[0],
          submission:        newApplicationDetail.submissions[0],
          applicationDetail: newApplicationDetail
        })
      })
    })

    //
    ;[
      [false, false, "before submissions are approved"],
      [true, false, "before the user finishes paying"],
      [true, true, "after payment is complete"]
    ].forEach(([submissionsComplete, hasPaid, desc]) => {
      it(`shows details about payment status ${desc}`, async () => {
        let newApplicationDetail = Object.assign({}, applicationDetail)
        if (!submissionsComplete) {
          newApplicationDetail = setToAwaitingReview(newApplicationDetail)
        } else {
          newApplicationDetail = hasPaid ?
            setToPaid(newApplicationDetail) :
            setToAwaitingPayment(newApplicationDetail)
        }
        const props = {
          ...defaultProps,
          allApplicationDetail: {
            [application.id]: newApplicationDetail
          }
        }
        const wrapper = await renderExpanded(props)

        const paymentDetail = wrapper.find("PaymentDetail")
        assert.isTrue(paymentDetail.exists())
        assert.deepEqual(paymentDetail.props(), {
          ready:             submissionsComplete,
          fulfilled:         hasPaid,
          openDrawer:        openDrawerStub,
          applicationDetail: newApplicationDetail
        })
      })
    })
  })
  ;[true, false].forEach(hasPayments => {
    it(`${shouldIf(
      hasPayments
    )} have a view statement link if hasPayments=${String(
      hasPayments
    )}`, async () => {
      fakeApplications.forEach(application => {
        application.has_payments = hasPayments
      })
      const { wrapper } = await renderPage()

      const link = wrapper.find(".view-statement a").at(0)
      if (hasPayments) {
        assert.equal(
          link.prop("href"),
          `/applications/${fakeApplicationDetail.id}/payment-history/`
        )
      } else {
        assert.isFalse(link.exists())
      }
    })
  })
})
