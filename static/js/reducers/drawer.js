// @Flow
import { createAction, createReducer } from "@reduxjs/toolkit"

export const setDrawerState = createAction("SET_DRAWER_STATE")
export const setDrawerOpen = createAction("SET_DRAWER_OPEN")
export const setDrawerMeta = createAction("SET_DRAWER_META")
export const openDrawer = createAction("OPEN_DRAWER")

type DrawerState = {
  drawerState: ?string,
  drawerOpen: boolean,
  drawerMeta: Object
}

export type DrawerChangePayload = {
  type: ?string,
  meta?: Object
}

export const drawer = createReducer(
  { drawerState: null, drawerOpen: false, drawerMeta: {} },
  {
    [setDrawerState]: (state: DrawerState, action: { payload: ?string }) => {
      state.drawerState = action.payload
    },
    [setDrawerOpen]: (state: DrawerState, action: { payload: boolean }) => {
      state.drawerOpen = action.payload
    },
    [setDrawerMeta]: (state: DrawerState, action: { payload: Object }) => {
      state.drawerMeta = action.payload
    },
    [openDrawer]: (
      state: DrawerState,
      action: { payload: DrawerChangePayload }
    ) => {
      state.drawerState = action.payload.type
      state.drawerMeta = action.payload.meta || {}
      state.drawerOpen = true
    }
  }
)
