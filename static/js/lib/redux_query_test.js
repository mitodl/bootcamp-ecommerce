import { assert } from "chai"

import { constructIdMap, isQueryInErrorState } from "./redux_query"

describe("Redux Query helper", () => {
  it("constructIdMap should return a map from a list", () => {
    const results = [
      { id: 1, content: "foo" },
      { id: 2, content: "bar" },
      { id: 3, content: "baz" }
    ]

    assert.deepEqual(constructIdMap(results), {
      1: results[0],
      2: results[1],
      3: results[2]
    })
  })
  ;[
    [null, false],
    [200, false],
    [300, false],
    [400, true],
    [500, true]
  ].forEach(([statusCode, expected]) => {
    it(`isQueryInErrorState should return ${String(
      expected
    )} when query status=${String(statusCode)}`, () => {
      const queryState = statusCode ?
        {
          status: statusCode
        } :
        null
      assert.equal(isQueryInErrorState(queryState), expected)
    })
  })
})
