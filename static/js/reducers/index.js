// @flow
import { combineReducers } from "redux"
import { entitiesReducer, queriesReducer } from "redux-query"

import ui from "./ui"
import { drawer } from "./drawer"

export default combineReducers<*, *>({
  entities: entitiesReducer,
  queries:  queriesReducer,
  ui,
  drawer
})
