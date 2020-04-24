// @flow
import { combineReducers } from "redux"
import { entitiesReducer, queriesReducer } from "redux-query"

import ui from "./ui"

export default combineReducers<*, *>({
  entities: entitiesReducer,
  queries:  queriesReducer,
  ui
})
