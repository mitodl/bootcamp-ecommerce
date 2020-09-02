/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"
import { connectRequest } from "redux-query-react"
import { createStructuredSelector } from "reselect"
import {
  Dropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem
} from "reactstrap"
import { partial } from "ramda"

import SupportLink from "./SupportLink"
import { closeDrawer } from "../reducers/drawer"
import users, { currentUserSelector } from "../lib/queries/users"
import bootcamps, { bootcampRunsSelector } from "../lib/queries/bootcamps"
import applications, { createAppQueryKey } from "../lib/queries/applications"
import { isQueryPending } from "../lib/queries/util"
import { isErrorResponse } from "../util/util"

import type { User } from "../flow/authTypes"
import type { BootcampRun } from "../flow/bootcampTypes"
import type { NewApplicationResponse } from "../flow/applicationTypes"
import ButtonWithLoader from "./loaders/ButtonWithLoader"

const noAvailableBootcampsMsg =
  "There are no bootcamps that are currently open for application."

type Props = {
  currentUser: User,
  bootcampRuns: ?Array<BootcampRun>,
  appliedRunIds: Array<number>,
  createAppIsPending: boolean,
  createNewApplication: (bootcampRunId: number) => void,
  closeDrawer: () => void
}

type State = {
  selectedBootcamp: ?BootcampRun,
  dropdownOpen: boolean,
  requestFailed: boolean
}

const INITIAL_STATE: State = {
  selectedBootcamp: null,
  dropdownOpen:     false,
  requestFailed:    false
}

export class NewApplication extends React.Component<Props, State> {
  state = { ...INITIAL_STATE }

  changeSelectedRun = (run: BootcampRun) => {
    this.setState({
      selectedBootcamp: run,
      requestFailed:    false
    })
  }

  handleSubmit = async () => {
    const { createNewApplication, closeDrawer } = this.props
    const { selectedBootcamp } = this.state

    if (!selectedBootcamp) {
      return
    }
    const response: NewApplicationResponse = await createNewApplication(
      selectedBootcamp.id
    )
    if (isErrorResponse(response)) {
      this.setState({ requestFailed: true })
      return
    }
    this.setState({ ...INITIAL_STATE })
    closeDrawer()
  }

  render() {
    const {
      currentUser,
      bootcampRuns,
      appliedRunIds,
      createAppIsPending
    } = this.props
    const { selectedBootcamp, dropdownOpen, requestFailed } = this.state

    if (!currentUser || !bootcampRuns) {
      return null
    }

    const unappliedBootcampRuns = bootcampRuns.filter(
      (bootcampRun: BootcampRun) => !appliedRunIds.includes(bootcampRun.id)
    )
    const items = unappliedBootcampRuns.map((bootcampRun: BootcampRun) => (
      <DropdownItem
        value={bootcampRun.run_key}
        key={bootcampRun.id}
        onClick={partial(this.changeSelectedRun, [bootcampRun])}
      >
        {bootcampRun.display_title}
      </DropdownItem>
    ))
    const dropdownText = selectedBootcamp ?
      selectedBootcamp.display_title :
      "Select..."

    return (
      <div className="container drawer-wrapper new-application-drawer">
        <h2 className="mb-3">Select Bootcamp</h2>
        {unappliedBootcampRuns.length === 0 ? (
          <p className="mb-3">{noAvailableBootcampsMsg}</p>
        ) : (
          <React.Fragment>
            <p className="mb-3">
              To apply to a bootcamp, please select from the list below and
              click Continue.
            </p>
            <label className="d-block font-weight-bold">Bootcamps</label>
            <Dropdown
              isOpen={dropdownOpen}
              toggle={() => this.setState({ dropdownOpen: !dropdownOpen })}
              className="mb-3 standard-select full-width"
            >
              <DropdownToggle caret>{dropdownText}</DropdownToggle>
              <DropdownMenu>{items}</DropdownMenu>
            </Dropdown>
            <div className="mb-3 d-flex justify-content-end">
              <ButtonWithLoader
                className="btn-red btn-inverse"
                onClick={this.handleSubmit}
                loading={createAppIsPending}
                disabled={createAppIsPending || !selectedBootcamp}
              >
                Continue
              </ButtonWithLoader>
            </div>
            {requestFailed && (
              <p className="form-error">
                Something went wrong while creating your application. Please
                refresh the page and try again, or <SupportLink />
              </p>
            )}
          </React.Fragment>
        )}
      </div>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  currentUser:        currentUserSelector,
  bootcampRuns:       bootcampRunsSelector,
  createAppIsPending: isQueryPending(createAppQueryKey)
})

const mapPropsToConfigs = () => [
  users.currentUserQuery(),
  bootcamps.bootcampRunsQuery()
]

const mapDispatchToProps = dispatch => ({
  createNewApplication: (bootcampRunId: number) =>
    dispatch(
      mutateAsync(applications.createApplicationMutation(bootcampRunId))
    ),
  closeDrawer: () => dispatch(closeDrawer())
})

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(NewApplication)
