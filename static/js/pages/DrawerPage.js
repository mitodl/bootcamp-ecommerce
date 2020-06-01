// @flow
import React from "react"
import { connect } from "react-redux"
import { useDispatch, useSelector } from "react-redux"

import Drawer from "../components/Drawer"

import { drawerSelector } from "../lib/selectors"
import { setDrawerOpen, setDrawerState } from "../reducers/drawer"
import EditProfileDisplay from "../components/EditProfileDisplay"
import ViewProfileDisplay from "../components/ViewProfileDisplay"
import { PROFILE_EDIT, PROFILE_VIEW } from "../constants"

type Props = {}

// $FlowFixMe: this is a temporary page
export function DrawerPage(props: Props) {
  const { setDrawerState } = props
  const { drawerState } = useSelector(drawerSelector)
  const dispatch = useDispatch()
  const closeDrawer = () => dispatch(setDrawerOpen(false))

  const openDrawer = state => {
    dispatch(setDrawerOpen(true))
    dispatch(setDrawerState(state))
  }

  const renderChild = () => {
    switch (drawerState) {
    case PROFILE_EDIT:
      return <EditProfileDisplay />
    case PROFILE_VIEW:
      return <ViewProfileDisplay />
    }
  }

  return (
    <>
      <Drawer className="align-right">{renderChild()}</Drawer>
      <ul>
        <li>
          <button onClick={() => closeDrawer()}>Close Drawer</button>
        </li>
        <li>
          <button onClick={() => openDrawer(PROFILE_EDIT)}>Edit Profile</button>
        </li>
        <li>
          <button onClick={() => openDrawer(PROFILE_VIEW)}>View Profile</button>
        </li>
      </ul>
    </>
  )
}

const mapStateToProps = state => ({
  drawerState: state.drawer.drawerState,
  drawerOpen:  state.drawer.drawerOpen
})

const mapDispatchToProps = dispatch => ({
  setDrawerState: (newState: ?string) => dispatch(setDrawerState(newState))
})

export default connect(mapStateToProps, mapDispatchToProps)(DrawerPage)
