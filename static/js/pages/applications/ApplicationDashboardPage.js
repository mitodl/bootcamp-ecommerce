// @flow
/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query-react"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import queries from "../../lib/queries"
import { applicationsSelector } from "../../lib/queries/applications"
import { currentUserSelector } from "../../lib/queries/users"
import { formatStartEndDateStrings, formatTitle } from "../../util/util"
import {
  APP_STATE_TEXT_MAP,
  APPLICATIONS_DASHBOARD_PAGE_TITLE
} from "../../constants"

import type { Application } from "../../flow/applicationTypes"
import type { User } from "../../flow/authTypes"

type Props = {
  applications: Array<Application>,
  currentUser: User
}

export class ApplicationDashboardPage extends React.Component<Props> {
  renderApplicationCard = (application: Application) => {
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

const mapStateToProps = () =>
  createStructuredSelector({
    applications: applicationsSelector,
    currentUser:  currentUserSelector
  })

const mapPropsToConfigs = () => [queries.applications.applicationsQuery()]

export default compose(
  connect(mapStateToProps),
  connectRequest(mapPropsToConfigs)
)(ApplicationDashboardPage)
