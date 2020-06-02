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
  PROFILE_VIEW
} from "../../constants"
import { setDrawerOpen, setDrawerState } from "../../reducers/drawer"

import type {
  Application,
  ApplicationDetailState
} from "../../flow/applicationTypes"
import type { User } from "../../flow/authTypes"

type Props = {
  applications: Array<Application>,
  allApplicationDetail: ApplicationDetailState,
  currentUser: User,
  fetchAppDetail: Function,
  setDrawerOpen: Function,
  setDrawerState: Function
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

  renderApplicationDetail = (applicationId: number) => {
    const { allApplicationDetail, setDrawerOpen, setDrawerState } = this.props

    if (!allApplicationDetail || !allApplicationDetail[String(applicationId)]) {
      return null
    }
    return (
      <div className="row application-detail">
        <div className="col-12 section-profile">
          <h3>Profile Information</h3>
          <a
            className="btn-link"
            onClick={() => {
              setDrawerState(PROFILE_VIEW)
              setDrawerOpen(true)
            }}
          >
            View/Edit Profile
          </a>
        </div>
        <div className="col-12">
          <h3>Resume or LinkedIn Profile</h3>
          <a className="btn-link">View/Edit Resume</a>
        </div>
        <div className="col-12">
          <h3>Video interview</h3>
          <a className="btn-link">Take Video Interview</a>
        </div>
        <div className="col-12">
          <h3>Application Review</h3>
        </div>
        <div className="col-12">
          <h3>Payment</h3>
          <a className="btn-link">Make a Payment</a>
        </div>
      </div>
    )
  }

  renderApplicationCard = (application: Application) => {
    const { collapseVisible } = this.state

    const isOpen = collapseVisible[String(application.id)]

    return (
      <div className="application-card container" key={application.id}>
        <div className="row justify-content-between">
          <div className="col-12 col-sm-8">
            <div className="row">
              {application.bootcamp_run.page &&
              application.bootcamp_run.page.thumbnail_image_src ? (
                  <div className="col-auto">
                    <img
                      src={application.bootcamp_run.page.thumbnail_image_src}
                      alt="Bootcamp thumbnail"
                    />
                  </div>
                ) : null}
              <div className="col-12 col-sm no-padding">
                <h2>{application.bootcamp_run.bootcamp.title}</h2>
                <div className="row run-details no-gutters">
                  <div className="col-auto col-sm-3 label">Location:</div>
                  <div className="col text">
                    &nbsp;<strong>Online</strong>
                  </div>
                  <div className="w-100" />
                  <div className="col-auto col-sm-3 label">Dates:</div>
                  <div className="col text">
                    &nbsp;
                    <strong>
                      {formatStartEndDateStrings(
                        application.bootcamp_run.start_date,
                        application.bootcamp_run.end_date
                      )}
                    </strong>
                  </div>
                  <div className="w-100" />
                </div>
              </div>
            </div>
          </div>

          <div className="col-12 col-sm-4 status-col">
            <span className="label">Application Status:</span>{" "}
            <strong>{APP_STATE_TEXT_MAP[application.state]}</strong>
          </div>
        </div>
        <div className="row text-right">
          <div className="col-12">
            <a
              className="btn-text expand-collapse"
              onClick={R.partial(this.loadAndRevealAppDetail, [application.id])}
            >
              {isOpen ? "Collapse −" : "Expand ＋"}
            </a>
          </div>
        </div>
        <Collapse isOpen={isOpen}>
          {this.renderApplicationDetail(application.id)}
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
  setDrawerOpen:  (newState: boolean) => dispatch(setDrawerOpen(newState)),
  setDrawerState: (newState: ?string) => dispatch(setDrawerState(newState))
})

const mapPropsToConfigs = () => [queries.applications.applicationsQuery()]

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(ApplicationDashboardPage)
