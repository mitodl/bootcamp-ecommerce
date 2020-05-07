// @flow
import { useCallback } from "react"
import * as React from "react"
import { useDispatch, useSelector } from "react-redux"
import { Drawer as RMWCDrawer, DrawerContent } from "@rmwc/drawer"
import { Theme } from "@rmwc/theme"
import { createSelector } from "reselect"

import { toggleDrawer } from "../reducers/drawer"

const drawerSelector = createSelector(
  state => state.drawer,
  drawer => drawer
)

type Props = {
  children?: React.Node
}

export default function Drawer(props: Props) {
  const { children } = props
  const { showDrawer } = useSelector(drawerSelector)

  const dispatch = useDispatch()
  const closeDrawer = useCallback(() => {
    dispatch(toggleDrawer())
  }, [dispatch])

  return (
    <Theme>
      <RMWCDrawer open={showDrawer} onClose={closeDrawer} dir="rtl" modal>
        <DrawerContent dir="ltr">{children}</DrawerContent>
      </RMWCDrawer>
    </Theme>
  )
}
