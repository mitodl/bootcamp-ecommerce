// @flow
/* global SETTINGS: false */
import React from "react"
import { shallow } from "enzyme"
import sinon from "sinon"
import { assert } from "chai"
import moment from "moment"

import {
  ProfileDetail,
  ResumeDetail,
  VideoInterviewDetail,
  ReviewDetail,
  PaymentDetail,
  BootcampStartDetail
} from "./detail_sections"
import {
  AWAITING_RESUME,
  AWAITING_USER_SUBMISSIONS,
  AWAITING_SUBMISSION_REVIEW,
  PAYMENT,
  PROFILE_VIEW,
  REVIEW_STATUS_APPROVED,
  REVIEW_STATUS_PENDING,
  REVIEW_STATUS_REJECTED,
  REVIEW_STATUS_WAITLISTED,
  SUBMISSION_VIDEO
} from "../../constants"
import * as utils from "../../util/util"
import IntegrationTestHelper from "../../util/integration_test_helper"
import { makeIncompleteUser } from "../../factories/user"
import {
  makeApplicationDetail,
  makeApplicationRunStep,
  makeApplicationSubmission
} from "../../factories/application"
import { isIf, shouldIf } from "../../lib/test_utils"

describe("application detail section component", () => {
  const fakeFormattedDate = "Jan 1st, 2020"
  const isoDate = moment().format()
  let helper, openDrawerStub, defaultProps

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    helper.sandbox
      .stub(utils, "formatReadableDateFromStr")
      .returns(fakeFormattedDate)
    openDrawerStub = sinon.spy()
    defaultProps = {
      ready:      false,
      fulfilled:  false,
      openDrawer: openDrawerStub
    }
  })

  afterEach(() => {
    helper.cleanup()
  })

  describe("ProfileDetail", () => {
    it("should include a link to view/edit a profile", () => {
      const wrapper = shallow(
        <ProfileDetail {...defaultProps} user={makeIncompleteUser()} />
      )
      wrapper.find("ProgressDetailRow button.btn-link").simulate("click")
      sinon.assert.calledWith(openDrawerStub, { type: PROFILE_VIEW })
    })
  })

  describe("ResumeDetail", () => {
    let applicationDetail
    beforeEach(() => {
      applicationDetail = makeApplicationDetail()
    })

    //
    ;[
      [false, false, AWAITING_RESUME, undefined],
      [true, false, AWAITING_RESUME, "Add Resume or LinkedIn Profile"],
      [
        true,
        false,
        AWAITING_USER_SUBMISSIONS,
        "Add Resume or LinkedIn Profile"
      ],
      [
        true,
        false,
        AWAITING_SUBMISSION_REVIEW,
        "Add Resume or LinkedIn Profile"
      ],
      [true, false, "AWAITING_PAYMENT", undefined],
      [true, true, AWAITING_RESUME, "View/Edit Resume or LinkedIn Profile"],
      [
        true,
        true,
        AWAITING_USER_SUBMISSIONS,
        "View/Edit Resume or LinkedIn Profile"
      ],
      [
        true,
        true,
        AWAITING_SUBMISSION_REVIEW,
        "View/Edit Resume or LinkedIn Profile"
      ],
      [true, true, "AWAITING_PAYMENT", undefined]
    ].forEach(([ready, fulfilled, state, expLinkText]) => {
      it(`should show correct link if ready === ${String(
        ready
      )}, fulfilled === ${String(fulfilled)}, state === ${state}`, () => {
        applicationDetail.state = state
        const wrapper = shallow(
          <ResumeDetail
            {...defaultProps}
            ready={ready}
            fulfilled={fulfilled}
            applicationDetail={applicationDetail}
          />
        )
        const link = wrapper.find("ProgressDetailRow button.btn-link")
        assert.equal(link.exists(), expLinkText !== undefined)
        if (expLinkText !== undefined) {
          assert.equal(link.prop("children"), expLinkText)
        }
      })
    })
  })

  describe("VideoInterviewDetail", () => {
    let step, submission, application
    beforeEach(() => {
      step = makeApplicationRunStep(SUBMISSION_VIDEO)
      submission = makeApplicationSubmission()
      application = makeApplicationDetail()
    })

    //
    ;[
      [false, false, false, undefined],
      [true, false, false, "Take Video Interview"],
      [true, true, false, undefined]
    ].forEach(([ready, fulfilled, submitted, expLinkText]) => {
      it(`should show correct link if ready === ${String(
        ready
      )}, fulfilled === ${String(fulfilled)}, and submitted = ${String(
        submitted
      )}`, () => {
        if (!submitted) {
          submission.interview_url = null
        }
        const wrapper = shallow(
          <VideoInterviewDetail
            {...defaultProps}
            ready={ready}
            fulfilled={fulfilled}
            step={step}
            submission={submission}
            applicationDetail={application}
          />
        )
        const link = wrapper.find(
          fulfilled ?
            "ProgressDetailRow a.btn-link" :
            "ProgressDetailRow button.btn-link"
        )
        assert.equal(link.exists(), expLinkText !== undefined)
        if (expLinkText !== undefined) {
          assert.equal(
            fulfilled ? link.text() : link.prop("children"),
            expLinkText
          )
        }
      })
    })
  })

  describe("ReviewDetail", () => {
    let step, submission, application
    beforeEach(() => {
      step = makeApplicationRunStep(SUBMISSION_VIDEO)
      submission = makeApplicationSubmission()
      application = makeApplicationDetail()
    })

    it("should show no status if the submission has no review", () => {
      const wrapper = shallow(
        <ReviewDetail
          {...defaultProps}
          step={step}
          submission={null}
          applicationDetail={application}
        />
      )

      assert.isFalse(wrapper.find("ProgressDetailRow .status-text").exists())
    })

    //
    ;[
      [REVIEW_STATUS_PENDING, null, "Pending"],
      [REVIEW_STATUS_WAITLISTED, null, "Pending"],
      [REVIEW_STATUS_REJECTED, isoDate, "Rejected"],
      [REVIEW_STATUS_APPROVED, isoDate, "Approved"]
    ].forEach(([reviewStatus, reviewDate, expLinkText]) => {
      it(`should show correct status if review status = ${reviewStatus} and review date ${isIf(
        !!reviewDate
      )} set`, () => {
        submission.review_status = reviewStatus
        submission.review_status_date = reviewDate
        const wrapper = shallow(
          <ReviewDetail
            {...defaultProps}
            step={step}
            submission={submission}
            applicationDetail={application}
          />
        )

        assert.equal(
          wrapper.find("ProgressDetailRow .status-text").text(),
          `Status: ${expLinkText}`
        )
      })
    })
  })

  describe("PaymentDetail", () => {
    let applicationDetail
    beforeEach(() => {
      applicationDetail = makeApplicationDetail()
    })
    //
    ;[
      [false, false, undefined],
      [true, false, "Make a Payment"],
      [true, true, undefined]
    ].forEach(([ready, fulfilled, expLinkText]) => {
      it(`should show correct link if ready === ${String(
        ready
      )}, fulfilled === ${String(fulfilled)}`, () => {
        const wrapper = shallow(
          <PaymentDetail
            {...defaultProps}
            ready={ready}
            fulfilled={fulfilled}
            applicationDetail={applicationDetail}
          />
        )
        const link = wrapper.find("ProgressDetailRow button.btn-link")
        assert.equal(link.exists(), expLinkText !== undefined)
        if (expLinkText !== undefined) {
          assert.equal(link.prop("children"), expLinkText)
        }
      })
    })

    it("should open a drawer if the 'make a payment' link is clicked", () => {
      const wrapper = shallow(
        <PaymentDetail
          {...defaultProps}
          ready={true}
          fulfilled={false}
          applicationDetail={applicationDetail}
        />
      )

      wrapper.find("ProgressDetailRow button.btn-link").simulate("click")
      sinon.assert.calledWith(openDrawerStub, {
        type: PAYMENT,
        meta: { application: applicationDetail }
      })
    })
  })

  describe("BootcampStartDetail", () => {
    let applicationDetail
    beforeEach(() => {
      applicationDetail = makeApplicationDetail()
    })
    //
    ;[
      [false, false, "", false, "not ready", undefined],
      [true, false, "", false, "not fulfilled", undefined],
      [true, true, "", false, "course stub is null", undefined],
      [
        true,
        true,
        "some-stub",
        true,
        "fulfilled with a valid course stub",
        "Start Bootcamp"
      ]
    ].forEach(([ready, fulfilled, novoEdStub, expLink, desc, expLinkText]) => {
      it(`${shouldIf(expLink)} show correct link if ${desc}`, () => {
        SETTINGS.novoed_base_url = "https://novoed.com"
        applicationDetail.bootcamp_run.novoed_course_stub = novoEdStub

        const wrapper = shallow(
          <BootcampStartDetail
            {...defaultProps}
            ready={ready}
            fulfilled={fulfilled}
            applicationDetail={applicationDetail}
          />
        )
        if (expLink) {
          const link = wrapper.find("ProgressDetailRow a")
          assert.equal(link.exists(), expLinkText !== undefined)
          assert.equal(link.prop("children"), expLinkText)
          assert.equal(
            link.prop("href"),
            `${SETTINGS.novoed_base_url}/#!/courses/${novoEdStub}/home`
          )
        }
      })
    })
  })
})
