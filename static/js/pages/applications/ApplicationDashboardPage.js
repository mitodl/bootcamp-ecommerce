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

import {
  PaymentDetail,
  ProfileDetail,
  QuizDetail,
  ResumeDetail,
  ReviewDetail,
  VideoInterviewDetail
} from "../../components/applications/detail_sections"
import { openDrawer } from "../../reducers/drawer"
import queries from "../../lib/queries"
import {
  applicationDetailSelector,
  applicationsSelector
} from "../../lib/queries/applications"
import { currentUserSelector } from "../../lib/queries/users"
import { formatStartEndDateStrings, formatTitle } from "../../util/util"
import {
  APP_STATE_TEXT_MAP,
  APPLICATIONS_DASHBOARD_PAGE_TITLE,
  SUBMISSION_VIDEO,
  SUBMISSION_QUIZ,
  REVIEW_STATUS_APPROVED
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
        stepFulfilled = appStepSubmissions[step.id] !== undefined
        submissionApproved =
          !!appStepSubmissions[step.id] &&
          appStepSubmissions[step.id].review_status === REVIEW_STATUS_APPROVED
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
          />,
          <ReviewDetail
            ready={true}
            fulfilled={submissionApproved}
            openDrawer={openDrawer}
            step={step}
            submission={appStepSubmissions[step.id]}
            key={`review-${step.step_order}`}
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

            <div className="row text-right">
              <div className="col-12 pt-2">
                <a
                  className="btn-text expand-collapse"
                  onClick={R.partial(this.loadAndRevealAppDetail, [
                    application.id
                  ])}
                >
                  {isOpen ? "Collapse −" : "Expand ＋"}
                </a>
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

    return applications && currentUser ? (
      <div className="container applications-page">
        <MetaTags>
          <title>{formatTitle(APPLICATIONS_DASHBOARD_PAGE_TITLE)}</title>
        </MetaTags>
        <h1>{APPLICATIONS_DASHBOARD_PAGE_TITLE}</h1>
        {currentUser.profile && currentUser.profile.name ? (
          <h2 className="name">{currentUser.profile.name}</h2>
        ) : null}
        {applications && applications.map(this.renderApplicationCard)}
      </div>
    ) : null
  }
}

const mapStateToProps = createStructuredSelector({
  applications:         applicationsSelector,
  allApplicationDetail: applicationDetailSelector,
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
