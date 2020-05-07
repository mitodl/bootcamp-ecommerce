// @flow
import { combineReducers } from "redux"
import { entitiesReducer, queriesReducer } from "redux-query"

import ui from "./ui"
import userNotifications from "./notifications"

export default combineReducers<*, *>({
  entities: entitiesReducer,
  queries:  queriesReducer,
  ui,
  userNotifications
})
