// @Flow
import { createAction, createReducer } from "@reduxjs/toolkit"

export const toggleDrawer = createAction("TOGGLE_DRAWER")

export const drawer = createReducer(
  { showDrawer: false },
  {
    [toggleDrawer]: state => {
      state.showDrawer = !state.showDrawer
    }
  }
)
