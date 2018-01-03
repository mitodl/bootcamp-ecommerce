import { assert } from "chai"
import type { Store } from "redux"

import type { Action } from "../flow/reduxTypes"

export function createAssertReducerResultState<State>(
  store: Store,
  getReducerState: (x: any) => State
) {
  return (
    action: () => Action<*, *>,
    stateLookup: (state: State) => any,
    defaultValue: any
  ): void => {
    const getState = () => stateLookup(getReducerState(store.getState()))

    assert.deepEqual(defaultValue, getState())
    for (const value of [
      true,
      null,
      false,
      0,
      3,
      "x",
      { a: "b" },
      {},
      [3, 4, 5],
      [],
      ""
    ]) {
      store.dispatch(action(value))
      assert.deepEqual(value, getState())
    }
  }
}
