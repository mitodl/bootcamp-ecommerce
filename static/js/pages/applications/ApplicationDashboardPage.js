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
import moment from "moment"
import wait from "waait"
import qs from "query-string"
import { reverse } from "named-urls"

import {
  BootcampStartDetail,
  PaymentDetail,
  ProfileDetail,
  QuizDetail,
  ResumeDetail,
  ReviewDetail,
  VideoInterviewDetail
} from "../../components/applications/detail_sections"
import ButtonWithLoader from "../../components/loaders/ButtonWithLoader"
import FullLoader from "../../components/loaders/FullLoader"
import SupportLink from "../../components/SupportLink"

import { addErrorNotification, addSuccessNotification } from "../../actions"
import { openDrawer } from "../../reducers/drawer"
import {
  findAppByRunTitle,
  isStatusPollingFinished
} from "../../lib/applicationApi"
import queries from "../../lib/queries"
import { isQueryInErrorState } from "../../lib/redux_query"
import {
  allApplicationDetailSelector,
  allApplicationDetailLoadingSelector,
  appDetailQuerySelector,
  applicationsSelector,
  applicationsLoadingSelector
} from "../../lib/queries/applications"
import { currentUserSelector } from "../../lib/queries/users"
import { routes } from "../../lib/urls"
import {
  formatStartEndDateStrings,
  formatTitle,
  isErrorResponse,
  isNilOrBlank
} from "../../util/util"
import {
  APP_STATE_TEXT_MAP,
  APPLICATIONS_DASHBOARD_PAGE_TITLE,
  SUBMISSION_VIDEO,
  SUBMISSION_QUIZ,
  SUBMISSION_STATUS_SUBMITTED,
  REVIEW_STATUS_APPROVED,
  NEW_APPLICATION,
  CYBERSOURCE_RETURN_QS_STATE,
  CYBERSOURCE_DECISION_ACCEPT
} from "../../constants"

import type { User } from "../../flow/authTypes"
import type {
  Application,
  ApplicationDetailResponse,
  ApplicationDetailState,
  ApplicationRunStep,
  ApplicationSubmission,
  ValidAppStepType
} from "../../flow/applicationTypes"
import type {
  CybersourcePayload,
  OrderResponse
} from "../../flow/ecommerceTypes"
import type { DrawerChangePayload } from "../../reducers/drawer"
import type { Location } from "react-router"
// $FlowFixMe: This export exists
import type { QueryState } from "redux-query"

declare var CSOURCE_PAYLOAD: ?CybersourcePayload

const NUM_MILLIS_PER_POLL = 3000
const NUM_POLL_ATTEMPTS = 10
const MAX_ORDER_AGE_MINUTES = 15

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
  location: Location,
  applications: Array<Application>,
  applicationsLoading: boolean,
  allApplicationDetail: ApplicationDetailState,
  allApplicationDetailLoading: { number: boolean },
  appDetailQueryStatus: (applicationId: string) => ?QueryState,
  currentUser: User,
  fetchAppDetail: (
    applicationId: string,
    force?: boolean
  ) => ?ApplicationDetailResponse,
  fetchOrder: (orderId: string) => OrderResponse,
  openDrawer: (actionPayload: DrawerChangePayload) => void,
  addSuccessNotification: (actionPayload: any) => void,
  addErrorNotification: (actionPayload: any) => void
}

type State = {
  collapseVisible: { string: boolean },
  pollingCount: number
}

export class ApplicationDashboardPage extends React.Component<Props, State> {
  state = {
    collapseVisible: {},
    pollingCount:    0
  }

  async componentDidMount() {
    const { applications } = this.props
    if (applications) {
      const orderId = this.getOrderIdFromCybersourceParams()
      if (orderId) {
        await this.handleCybersourcePageLoad(orderId)
      }
    }
  }

  async componentDidUpdate(prevProps: Props, prevState: State) {
    const { pollingCount } = this.state
    if (
      prevProps.applications !== this.props.applications ||
      prevState.pollingCount !== pollingCount
    ) {
      const orderId = this.getOrderIdFromCybersourceParams()
      if (orderId) {
        if (pollingCount === 0) {
          await this.handleCybersourcePageLoad(orderId)
        } else if (prevState.pollingCount !== pollingCount) {
          await this.checkForOrderCompletion(orderId)
        }
      }
    }
  }

  getOrderIdFromCybersourceParams = (): ?string => {
    const { location } = this.props

    if (isNilOrBlank(location.search)) {
      return
    }
    // This page load should only be considered a Cybersource redirect if it has
    // the correct querystring params, and a global var containing some order metadata exists.
    const query = qs.parse(location.search)
    if (
      !query.status ||
      query.status !== CYBERSOURCE_RETURN_QS_STATE ||
      isNilOrBlank(query.order)
    ) {
      return
    }
    // We only need the order ID if the order date in the metadata is "fresh" enough. We can ignore
    // it otherwise.
    if (!CSOURCE_PAYLOAD || !CSOURCE_PAYLOAD.purchase_date_utc) {
      return
    }
    const orderDate = moment.utc(CSOURCE_PAYLOAD.purchase_date_utc)
    if (
      moment
        .utc()
        .subtract(MAX_ORDER_AGE_MINUTES, "minutes")
        .isAfter(orderDate)
    ) {
      return
    }
    return query.order
  }

  handleCybersourcePageLoad = async (orderId: string) => {
    const { addSuccessNotification, addErrorNotification } = this.props

    if (!CSOURCE_PAYLOAD) {
      return
    }
    const succeeded = CSOURCE_PAYLOAD.decision === CYBERSOURCE_DECISION_ACCEPT
    const notificationAction = succeeded ?
      addSuccessNotification :
      addErrorNotification
    const msg = succeeded ? (
      "Thank you! You will receive an email when your payment is successfully processed."
    ) : (
      <span>
        Something went wrong while processing your payment. Please{" "}
        <SupportLink className="alert-link" />
      </span>
    )
    notificationAction({
      props: {
        text: msg
      }
    })
    if (succeeded) {
      await this.checkForOrderCompletion(orderId)
    }
  }

  checkForOrderCompletion = async (orderId: string) => {
    const {
      applications,
      allApplicationDetail,
      fetchOrder,
      fetchAppDetail,
      addSuccessNotification,
      addErrorNotification
    } = this.props
    const { pollingCount } = this.state

    let succeeded
    if (pollingCount < NUM_POLL_ATTEMPTS) {
      const response = await fetchOrder(orderId)
      if (!isStatusPollingFinished(response)) {
        await wait(NUM_MILLIS_PER_POLL)
        this.setState({ pollingCount: pollingCount + 1 })
        return
      }
      succeeded = !isErrorResponse(response)
    } else {
      succeeded = false
    }
    const notificationAction = succeeded ?
      addSuccessNotification :
      addErrorNotification
    const msg = succeeded ? (
      "Your payment was processed successfully!"
    ) : (
      <span>
        Something went wrong while processing your payment. Please{" "}
        <SupportLink className="alert-link" />
      </span>
    )
    notificationAction({
      props: {
        text: msg
      }
    })
    if (!succeeded || !CSOURCE_PAYLOAD) {
      return
    }

    // If any application details have already been loaded, reload the details for the application
    // to which the successful order belongs.
    const runTitle = CSOURCE_PAYLOAD.bootcamp_run_purchased
    const appToUpdate = findAppByRunTitle(applications, runTitle)
    const applicationId = appToUpdate ? String(appToUpdate.id) : null
    if (
      allApplicationDetail &&
      applicationId &&
      allApplicationDetail[applicationId]
    ) {
      await fetchAppDetail(applicationId, true)
    }
  }

  onCollapseToggle = (applicationId: string): void => {
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

  loadAndRevealAppDetail = async (applicationId: string) => {
    const {
      fetchAppDetail,
      addErrorNotification,
      appDetailQueryStatus
    } = this.props
    const { collapseVisible } = this.state
    if (!collapseVisible[applicationId]) {
      const force = isQueryInErrorState(appDetailQueryStatus(applicationId))
      const response = await fetchAppDetail(applicationId, force)
      if (response && isErrorResponse(response)) {
        addErrorNotification({
          props: {
            text: (
              <span>
                Something went wrong while loading your application details.
                Please try again, or <SupportLink className="alert-link" />
              </span>
            )
          }
        })
        return
      }
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

    const profileAndAddressFulfilled =
      !!currentUser.profile &&
      currentUser.profile.is_complete &&
      !!currentUser.legal_address &&
      currentUser.legal_address.is_complete

    const profileRow = (
      <ProfileDetail
        ready={true}
        fulfilled={profileAndAddressFulfilled}
        openDrawer={openDrawer}
        user={currentUser}
      />
    )

    const resumeFulfilled = !!applicationDetail.resume_upload_date
    const resumeRow = (
      <ResumeDetail
        ready={profileAndAddressFulfilled}
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

    const isNovoEdCourse = !!applicationDetail.bootcamp_run.novoed_course_stub
    const novoEdEnrolled =
      isNovoEdCourse &&
      !!SETTINGS.novoed_login_url &&
      !!applicationDetail.enrollment &&
      !!applicationDetail.enrollment.novoed_sync_date
    const bootcampStartRow = isNovoEdCourse ? (
      <BootcampStartDetail
        ready={novoEdEnrolled}
        fulfilled={novoEdEnrolled}
        applicationDetail={applicationDetail}
      />
    ) : null

    return (
      <div className="p-3 mt-3 application-detail">
        {profileRow}
        {resumeRow}
        {submissionStepRows}
        {paymentRow}
        {bootcampStartRow}
      </div>
    )
  }

  renderApplicationCard = (application: Application) => {
    const { collapseVisible } = this.state
    const { allApplicationDetailLoading } = this.props

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
                <ButtonWithLoader
                  className="btn-text borderless expand-collapse"
                  aria-expanded={isOpen ? "true" : "false"}
                  onClick={R.partial(this.loadAndRevealAppDetail, [
                    String(application.id)
                  ])}
                  loading={!!allApplicationDetailLoading[application.id]}
                >
                  {isOpen ? "Collapse −" : "Expand ＋"}
                </ButtonWithLoader>
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
    const { currentUser, applications, applicationsLoading } = this.props

    if (!currentUser) {
      return null
    }

    const hasApplications = applications && applications.length > 0

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
            {applicationsLoading ? (
              <FullLoader />
            ) : hasApplications ? (
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
  applications:                applicationsSelector,
  applicationsLoading:         applicationsLoadingSelector,
  allApplicationDetail:        allApplicationDetailSelector,
  allApplicationDetailLoading: allApplicationDetailLoadingSelector,
  currentUser:                 currentUserSelector,
  appDetailQueryStatus:        appDetailQuerySelector
})

const mapDispatchToProps = dispatch => ({
  fetchAppDetail: async (applicationId: string, force?: boolean) =>
    dispatch(
      requestAsync(
        queries.applications.applicationDetailQuery(
          String(applicationId),
          !!force
        )
      )
    ),
  fetchOrder: async (orderId: string) =>
    dispatch(requestAsync(queries.ecommerce.orderQuery(orderId))),
  openDrawer: (actionPayload: DrawerChangePayload) =>
    dispatch(openDrawer(actionPayload)),
  addSuccessNotification: actionPayload =>
    dispatch(addSuccessNotification(actionPayload)),
  addErrorNotification: actionPayload =>
    dispatch(addErrorNotification(actionPayload))
})

const mapPropsToConfigs = () => [queries.applications.applicationsQuery()]

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(ApplicationDashboardPage)
