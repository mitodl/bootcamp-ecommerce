// @Flow
import { createAction, createReducer } from "@reduxjs/toolkit"

export const setDrawerState = createAction("SET_DRAWER_STATE")
export const setDrawerMeta = createAction("SET_DRAWER_META")
export const openDrawer = createAction("OPEN_DRAWER")
export const closeDrawer = createAction("CLOSE_DRAWER")

const initialState = {
  drawerState: null,
  drawerOpen:  false,
  drawerMeta:  {}
}

export const drawer = createReducer(initialState, builder => {
  builder
    .addCase(setDrawerState, (state, action) => {
      state.drawerState = action.payload
    })
    .addCase(setDrawerMeta, (state, action) => {
      state.drawerMeta = action.payload
    })
    .addCase(closeDrawer, state => {
      state.drawerState = null
      state.drawerMeta = {}
      state.drawerOpen = false
    })
    .addCase(openDrawer, (state, action) => {
      state.drawerState = action.payload.type
      state.drawerMeta = action.payload.meta || {}
      state.drawerOpen = true
    })
})
