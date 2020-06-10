// @Flow
import { createAction, createReducer } from "@reduxjs/toolkit"

export const setDrawerState = createAction("SET_DRAWER_STATE")
export const setDrawerOpen = createAction("SET_DRAWER_OPEN")
export const setDrawerMeta = createAction("SET_DRAWER_META")

export const drawer = createReducer(
  { drawerState: null, drawerOpen: false },
  {
    [setDrawerState]: (state, action) => {
      state.drawerState = action.payload
    },
    [setDrawerOpen]: (state, action) => {
      state.drawerOpen = action.payload
    },
    [setDrawerMeta]: (state, action) => {
      state.drawerMeta = action.payload
    }
  }
)
