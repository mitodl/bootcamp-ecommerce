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

import { setDrawerOpen } from "../reducers/drawer"
import users, { currentUserSelector } from "../lib/queries/users"
import bootcamps, { bootcampRunsSelector } from "../lib/queries/bootcamps"
import applications, { createAppQueryKey } from "../lib/queries/applications"
import { isQueryPending } from "../lib/queries/util"

import type { User } from "../flow/authTypes"
import type { BootcampRun } from "../flow/bootcampTypes"

const noAvailableBootcampsMsg =
  "There are no bootcamps that are currently open for application."

type Props = {
  currentUser: User,
  bootcampRuns: ?Array<BootcampRun>,
  appliedRunIds: Array<number>,
  createAppIsPending: boolean,
  createNewApplication: (bootcampRunId: number) => void,
  setDrawerOpen: (newState: boolean) => void
}

type State = {
  selectedBootcamp: ?BootcampRun,
  dropdownOpen: boolean
}

const INITIAL_STATE: State = {
  selectedBootcamp: null,
  dropdownOpen:     false
}

export class NewApplication extends React.Component<Props, State> {
  state = { ...INITIAL_STATE }

  changeSelectedRun = (run: BootcampRun) => {
    this.setState({
      selectedBootcamp: run
    })
  }

  handleSubmit = async () => {
    const { createNewApplication, setDrawerOpen } = this.props
    const { selectedBootcamp } = this.state

    if (!selectedBootcamp) {
      return
    }
    await createNewApplication(selectedBootcamp.id)
    this.setState({ ...INITIAL_STATE })
    setDrawerOpen(false)
  }

  render() {
    const {
      currentUser,
      bootcampRuns,
      appliedRunIds,
      createAppIsPending
    } = this.props
    const { selectedBootcamp, dropdownOpen } = this.state

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
        <h1 className="mb-3">Select Bootcamp</h1>
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
            <div className="d-flex justify-content-end">
              <button
                className="btn-red btn-inverse"
                onClick={this.handleSubmit}
                disabled={createAppIsPending || !selectedBootcamp}
              >
                Continue
              </button>
            </div>
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
  setDrawerOpen: (newState: boolean) => dispatch(setDrawerOpen(newState))
})

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(NewApplication)
