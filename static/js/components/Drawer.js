// @flow
import { useCallback } from "react"
import * as React from "react"
import { useDispatch, useSelector } from "react-redux"
import { Drawer as RMWCDrawer, DrawerContent } from "@rmwc/drawer"
import { Theme } from "@rmwc/theme"

import { drawerSelector } from "../lib/selectors"
import { setDrawerOpen } from "../reducers/drawer"

type Props = {
  children?: React.Node
}

export default function Drawer(props: Props) {
  const { children } = props
  const { drawerOpen } = useSelector(drawerSelector)

  const dispatch = useDispatch()
  const closeDrawer = useCallback(() => {
    dispatch(setDrawerOpen(false))
  }, [dispatch])

  return (
    <Theme>
      <RMWCDrawer open={drawerOpen} onClose={closeDrawer} dir="rtl" modal>
        <DrawerContent dir="ltr">{children}</DrawerContent>
      </RMWCDrawer>
    </Theme>
  )
}
