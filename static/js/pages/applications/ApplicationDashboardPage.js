// @flow
/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { requestAsync } from "redux-query"
import { connectRequest } from "redux-query-react"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"
import { Collapse } from "reactstrap"
import * as R from "ramda"
import { reverse } from "named-urls"

import {
  PaymentDetail,
  ProfileDetail,
  QuizDetail,
  ResumeDetail,
  ReviewDetail,
  VideoInterviewDetail
} from "../../components/applications/detail_sections"
import AccessibleAnchor from "../../components/AccessibleAnchor"

import { openDrawer } from "../../reducers/drawer"
import queries from "../../lib/queries"
import {
  allApplicationDetailSelector,
  applicationsSelector
} from "../../lib/queries/applications"
import { currentUserSelector } from "../../lib/queries/users"
import { formatStartEndDateStrings, formatTitle } from "../../util/util"
import { routes } from "../../lib/urls"
import {
  APP_STATE_TEXT_MAP,
  APPLICATIONS_DASHBOARD_PAGE_TITLE,
  SUBMISSION_VIDEO,
  SUBMISSION_QUIZ,
  SUBMISSION_STATUS_SUBMITTED,
  REVIEW_STATUS_APPROVED,
  NEW_APPLICATION
} from "../../constants"

import type {
  Application,
  ApplicationDetailState,
  ApplicationRunStep,
  ApplicationSubmission,
  ValidAppStepType
} from "../../flow/applicationTypes"
import type { User } from "../../flow/authTypes"
import type { DrawerChangePayload } from "../../reducers/drawer"

/*
 * Returns an object mapping an application step id to the user's submission (if anything was submitted
 * for that step).
 */
const getAppStepSubmissions = (
  runApplicationSteps: Array<ApplicationRunStep>,
  submissions: Array<ApplicationSubmission>
): { [number]: ?ApplicationSubmission } =>
  R.fromPairs(
    runApplicationSteps.map((step: ApplicationRunStep) => [
      step.id,
      submissions.find(
        (submission: ApplicationSubmission) =>
          submission.run_application_step_id === step.id
      )
    ])
  )

type Props = {
  applications: Array<Application>,
  allApplicationDetail: ApplicationDetailState,
  currentUser: User,
  fetchAppDetail: (applicationId: number) => void,
  openDrawer: (actionPayload: DrawerChangePayload) => void
}

type State = {
  collapseVisible: Object
}

export class ApplicationDashboardPage extends React.Component<Props, State> {
  state = {
    collapseVisible: {}
  }

  onCollapseToggle = (applicationId: number): void => {
    this.setState({
      collapseVisible: {
        ...this.state.collapseVisible,
        [applicationId]: !this.state.collapseVisible[applicationId]
      }
    })
  }

  onNewApplicationClick = (): void => {
    const { applications, openDrawer } = this.props

    const appliedRunIds = applications.map(
      (application: Application) => application.bootcamp_run.id
    )
    openDrawer({
      type: NEW_APPLICATION,
      meta: { appliedRunIds }
    })
  }

  loadAndRevealAppDetail = async (applicationId: number) => {
    const { fetchAppDetail } = this.props
    const { collapseVisible } = this.state
    if (!collapseVisible[applicationId]) {
      await fetchAppDetail(applicationId)
    }
    this.onCollapseToggle(applicationId)
  }

  SUBMISSION_STEP_COMPONENTS: { [ValidAppStepType]: React$ComponentType<*> } = {
    [SUBMISSION_VIDEO]: VideoInterviewDetail,
    [SUBMISSION_QUIZ]:  QuizDetail
  }

  renderApplicationDetailSection = (application: Application) => {
    const { allApplicationDetail, currentUser, openDrawer } = this.props

    if (
      !allApplicationDetail ||
      !allApplicationDetail[String(application.id)]
    ) {
      return null
    }
    const applicationDetail = allApplicationDetail[String(application.id)]
    const appStepSubmissions = getAppStepSubmissions(
      applicationDetail.run_application_steps,
      applicationDetail.submissions
    )

    const profileFulfilled =
      !!currentUser.profile && currentUser.profile.is_complete
    const profileRow = (
      <ProfileDetail
        ready={true}
        fulfilled={profileFulfilled}
        openDrawer={openDrawer}
        user={currentUser}
      />
    )

    const resumeFulfilled = !!applicationDetail.resume_upload_date
    const resumeRow = (
      <ResumeDetail
        ready={profileFulfilled}
        fulfilled={resumeFulfilled}
        openDrawer={openDrawer}
        applicationDetail={applicationDetail}
      />
    )

    let stepFulfilled, submissionApproved
    const submissionStepRows = applicationDetail.run_application_steps.map(
      (step: ApplicationRunStep) => {
        // If this is the first required submission, the user should only be able
        // to submit something if the resume step has been completed. Otherwise, they should
        // only be able to submit something if their previous submission was approved.
        const stepReady =
          stepFulfilled === undefined ? resumeFulfilled : stepFulfilled
        stepFulfilled = !!(
          appStepSubmissions[step.id] &&
          appStepSubmissions[step.id].submission_status ===
            SUBMISSION_STATUS_SUBMITTED
        )
        submissionApproved = !!(
          appStepSubmissions[step.id] &&
          appStepSubmissions[step.id].review_status === REVIEW_STATUS_APPROVED
        )
        const SubmissionComponent = this.SUBMISSION_STEP_COMPONENTS[
          step.submission_type
        ]
        return [
          <SubmissionComponent
            ready={stepReady}
            fulfilled={stepFulfilled}
            openDrawer={openDrawer}
            step={step}
            submission={appStepSubmissions[step.id]}
            key={`submission-${step.step_order}`}
            applicationDetail={applicationDetail}
          />,
          <ReviewDetail
            ready={true}
            fulfilled={submissionApproved}
            openDrawer={openDrawer}
            step={step}
            submission={appStepSubmissions[step.id]}
            key={`review-${step.step_order}`}
            applicationDetail={applicationDetail}
          />
        ]
      }
    )

    // If there are no submissions required for this application, payment should be ready after the resume
    // requirement is fulfilled. Otherwise, it should only be ready if the last submission was approved.
    const paymentReady =
      submissionApproved === undefined ? resumeFulfilled : submissionApproved
    const paymentRow = (
      <PaymentDetail
        ready={paymentReady}
        fulfilled={applicationDetail.is_paid_in_full}
        openDrawer={openDrawer}
        applicationDetail={applicationDetail}
      />
    )

    return (
      <div className="p-3 mt-3 application-detail">
        {profileRow}
        {resumeRow}
        {submissionStepRows}
        {paymentRow}
      </div>
    )
  }

  renderApplicationCard = (application: Application) => {
    const { collapseVisible } = this.state

    const isOpen = collapseVisible[String(application.id)]
    const thumbnailSrc = application.bootcamp_run.page ?
      application.bootcamp_run.page.thumbnail_image_src :
      null

    return (
      <div className="application-card" key={application.id}>
        <div className="p-3 d-flex flex-wrap flex-sm-nowrap">
          {thumbnailSrc && <img src={thumbnailSrc} alt="Bootcamp thumbnail" />}

          <div className="container p-0 pt-3 pt-sm-0 pl-sm-3 application-card-top">
            <div className="row">
              <div className={`col-12 col-md-6 mr-auto no-padding`}>
                <h2>{application.bootcamp_run.bootcamp.title}</h2>
                <div className="run-details">
                  <div>
                    <span className="label">Location:</span>{" "}
                    <strong className="text">Online</strong>
                  </div>
                  <div>
                    <span className="label">Dates:</span>{" "}
                    <strong className="text">
                      {formatStartEndDateStrings(
                        application.bootcamp_run.start_date,
                        application.bootcamp_run.end_date
                      )}
                    </strong>
                  </div>
                </div>
              </div>

              <div className="col-12 col-sm-auto text-sm-right status-col">
                <span className="label">Application Status:</span>{" "}
                <strong>{APP_STATE_TEXT_MAP[application.state]}</strong>
              </div>
            </div>
            <div className="row mt-2">
              <div className="col-7 text-left text-sm-right view-statement">
                {application.has_payments && (
                  <a
                    className="btn-link"
                    href={reverse(routes.applications.paymentHistory.self, {
                      applicationId: application.id
                    })}
                  >
                    <span className="material-icons">printer</span>
                    View Statement
                  </a>
                )}
              </div>
              <div className="col-5 text-right collapse-link">
                <AccessibleAnchor
                  className="btn-text expand-collapse"
                  onClick={R.partial(this.loadAndRevealAppDetail, [
                    application.id
                  ])}
                >
                  {isOpen ? "Collapse −" : "Expand ＋"}
                </AccessibleAnchor>
              </div>
            </div>
          </div>
        </div>

        <Collapse isOpen={isOpen}>
          {this.renderApplicationDetailSection(application)}
        </Collapse>
      </div>
    )
  }

  render() {
    const { currentUser, applications } = this.props

    if (!applications || !currentUser) {
      return null
    }

    const hasApplications = applications.length > 0

    return (
      <div className="container applications-page">
        <MetaTags>
          <title>{formatTitle(APPLICATIONS_DASHBOARD_PAGE_TITLE)}</title>
        </MetaTags>
        <div className="row justify-content-between">
          <div
            className={`col-12 ${hasApplications ? "col-md-7 col-lg-8" : ""}`}
          >
            <h1 className="m-0">{APPLICATIONS_DASHBOARD_PAGE_TITLE}</h1>
            {currentUser.profile && currentUser.profile.name ? (
              <h2 className="mt-4 mb-0 name">{currentUser.profile.name}</h2>
            ) : null}
          </div>
          {hasApplications && (
            <div className="col-12 col-md-5 col-lg-4 mt-4 mt-md-0 text-md-right">
              <div className="mb-1 caption">
                Interested in another bootcamp?
              </div>
              <button
                className="btn-red btn-inverse new-application-btn"
                onClick={this.onNewApplicationClick}
              >
                Select Bootcamp
              </button>
            </div>
          )}
        </div>
        <div className="row mt-4">
          <div className="col-12">
            {hasApplications ? (
              applications.map(this.renderApplicationCard)
            ) : (
              <React.Fragment>
                <p>
                  Thank you for registering and welcome to MIT Bootcamps.
                  <br />
                  Please click the button below to select the bootcamp you wish
                  to apply to.
                </p>
                <button
                  className="btn-red btn-inverse new-application-btn"
                  onClick={this.onNewApplicationClick}
                >
                  Select Bootcamp
                </button>
              </React.Fragment>
            )}
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  applications:         applicationsSelector,
  allApplicationDetail: allApplicationDetailSelector,
  currentUser:          currentUserSelector
})

const mapDispatchToProps = dispatch => ({
  fetchAppDetail: async (applicationId: number) =>
    dispatch(
      requestAsync(
        queries.applications.applicationDetailQuery(String(applicationId))
      )
    ),
  openDrawer: (actionPayload: DrawerChangePayload) =>
    dispatch(openDrawer(actionPayload))
})

const mapPropsToConfigs = () => [queries.applications.applicationsQuery()]

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(ApplicationDashboardPage)
