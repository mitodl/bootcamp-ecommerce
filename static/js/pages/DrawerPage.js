// @flow
import React, {useCallback} from "react"
import { connect } from "react-redux"
import { useDispatch, useSelector } from "react-redux"

import Drawer from "../components/Drawer"

import { drawerSelector } from "../lib/selectors"
import { setDrawerOpen, setDrawerState } from "../reducers/drawer"

type Props = {
}

export function DrawerPage(props: Props) {
  const { drawerOpen, drawerState } = useSelector(drawerSelector)
  const dispatch = useDispatch()
  const closeDrawer = () =>
    dispatch(setDrawerOpen(false))

  const openDrawer = (state) => {
    dispatch(setDrawerOpen(true))
    dispatch(setDrawerState(state))
  }


  return <>
    <Drawer>
      {drawerState}
    </Drawer>
    <ul>
      <li><button onClick={() => closeDrawer()}>Close Drawer</button></li>
      <li><button onClick={() => openDrawer("a")}>Open Drawer State A</button></li>
      <li><button onClick={() => openDrawer("b")}>Open Drawer State B</button></li>
    </ul>
  </>
}

const mapStateToProps = state => ({
  drawerState: state.drawer.drawerState,
  drawerOpen:  state.drawer.drawerOpen,
})

const mapDispatchToProps = dispatch => ({
  setDrawerState: (newState: ?string) => dispatch(setDrawerState(newState))
})

export default connect(mapStateToProps, mapDispatchToProps)(DrawerPage)
