// @flow
import { useCallback } from "react"
import * as React from "react"
import { useDispatch, useSelector } from "react-redux"
import { Drawer as RMWCDrawer, DrawerContent } from "@rmwc/drawer"
import { Theme } from "@rmwc/theme"

import { drawerSelector } from "../lib/selectors"
import { setDrawerOpen } from "../reducers/drawer"
import { PAYMENT, PROFILE_EDIT, PROFILE_VIEW } from "../constants"

import EditProfileDisplay from "./EditProfileDisplay"
import ViewProfileDisplay from "./ViewProfileDisplay"
import PaymentDisplay from "./PaymentDisplay"

const renderDrawerContents = (drawerState: string): ?React$Element<*> => {
  switch (drawerState) {
  case PROFILE_EDIT:
    return <EditProfileDisplay />
  case PROFILE_VIEW:
    return <ViewProfileDisplay />
  case PAYMENT:
    return <PaymentDisplay />
  default:
    return null
  }
}

export default function Drawer() {
  const { drawerOpen, drawerState } = useSelector(drawerSelector)

  const dispatch = useDispatch()
  const closeDrawer = useCallback(() => {
    dispatch(setDrawerOpen(false))
  }, [dispatch])

  return (
    <Theme>
      <RMWCDrawer open={drawerOpen} onClose={closeDrawer} dir="rtl" modal>
        <DrawerContent dir="ltr">
          {renderDrawerContents(drawerState)}
        </DrawerContent>
      </RMWCDrawer>
    </Theme>
  )
}
