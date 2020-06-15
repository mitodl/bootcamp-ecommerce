// @flow
import { nthArg, pathOr } from "ramda"

/*
 * Replaces the previous state with the next state without merging. For use in an "update" function in a redux-query
 * config. Using this function means that once you get data back from a query, you no longer need any data that was
 * previously loaded for that query.
 */
export const nextState = nthArg(1)

/*
 * Produces a function that takes the redux state and tells you if the query with the given key is currently pending.
 * Defaults to false.
 */
export const isQueryPending = (queryKey: string): boolean =>
  pathOr(false, ["queries", queryKey, "isPending"])

/*
 * Produces a function that takes the redux state and tells you if the query with the given key is finished.
 * Defaults to false.
 */
export const isQueryFinished = (queryKey: string): boolean =>
  pathOr(false, ["queries", queryKey, "isFinished"])
