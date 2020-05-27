// @Flow
import { createAction, createReducer } from "@reduxjs/toolkit"

export const setDrawerState = createAction("SET_DRAWER_STATE")
export const setDrawerOpen = createAction("SET_DRAWER_OPEN")

export const drawer = createReducer(
  { drawerState: null, drawerOpen: false },
  {
    [setDrawerState]: (state, action) => {
      state.drawerState = action.payload
    },
    [setDrawerOpen]: (state, action) => {
      state.drawerOpen = action.payload
    }
  }
)
