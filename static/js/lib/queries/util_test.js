import { assert } from "chai";

import { isQueryPending, isQueryFinished } from "./util";

describe("Redux-query util", () => {
  const fakeQueryKey = "myQuery";

  it("isQueryPending indicates whether or not a query is pending", () => {
    let result,
      state = {};
    result = isQueryPending(fakeQueryKey)(state);
    assert.isFalse(result);
    state = {
      queries: {
        [fakeQueryKey]: {
          isPending: false,
        },
      },
    };
    result = isQueryPending(fakeQueryKey)(state);
    assert.isFalse(result);
    state.queries[fakeQueryKey].isPending = true;
    result = isQueryPending(fakeQueryKey)(state);
    assert.isTrue(result);
  });

  it("isQueryFinished indicates whether or not a query is finished", () => {
    let result,
      state = {};
    result = isQueryFinished(fakeQueryKey)(state);
    assert.isFalse(result);
    state = {
      queries: {
        [fakeQueryKey]: {
          isFinished: false,
        },
      },
    };
    result = isQueryFinished(fakeQueryKey)(state);
    assert.isFalse(result);
    state.queries[fakeQueryKey].isFinished = true;
    result = isQueryFinished(fakeQueryKey)(state);
    assert.isTrue(result);
  });
});
