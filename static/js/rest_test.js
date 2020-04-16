import { createAction } from "redux-actions"
import sinon from "sinon"
import configureTestStore from "redux-asserts"
import { assert } from "chai"

import * as api from "./lib/api"
import { FETCH_PROCESSING, FETCH_SUCCESS, FETCH_FAILURE } from "./actions"
import {
  endpoints,
  makeAction,
  makeReducer,
  makeRequestActionType,
  makeReceiveSuccessActionType,
  makeReceiveFailureActionType,
  makeClearType
} from "./rest"

describe("rest", () => {
  const fakeEndpoint = {
    name:         "fake",
    url:          "/api/v0/fake/",
    fetchOptions: params => ({
      method: "POST",
      body:   JSON.stringify({
        param1: params.param1,
        param2: params.param2
      })
    })
  }

  let store
  beforeEach(() => {
    store = configureTestStore(makeReducer(fakeEndpoint))
  })

  afterEach(() => {
    sinon.restore()
  })

  describe("makeReducer", () => {
    it("has an initial state", () => {
      const initialState = { initial: "state" }
      const storeWithState = configureTestStore(
        makeReducer(fakeEndpoint, initialState)
      )
      assert.deepEqual(storeWithState.getState(), initialState)
    })

    it("handles a request action", () => {
      store.dispatch(createAction(makeRequestActionType(fakeEndpoint.name))())
      assert.deepEqual(store.getState(), {
        fetchStatus: FETCH_PROCESSING,
        loaded:      false,
        processing:  true
      })
    })

    it("handles a receive success action", () => {
      store.dispatch(
        createAction(makeReceiveSuccessActionType(fakeEndpoint.name))("data")
      )
      assert.deepEqual(store.getState(), {
        fetchStatus: FETCH_SUCCESS,
        loaded:      true,
        processing:  false,
        data:        "data"
      })
    })

    it("handles a receive failure action", () => {
      store.dispatch(
        createAction(makeReceiveFailureActionType(fakeEndpoint.name))("error")
      )
      assert.deepEqual(store.getState(), {
        fetchStatus: FETCH_FAILURE,
        loaded:      true,
        processing:  false,
        error:       "error"
      })
    })

    it("handles a clear action", () => {
      store.dispatch(createAction(makeRequestActionType(fakeEndpoint.name))())
      store.dispatch(createAction(makeClearType(fakeEndpoint.name))())
      assert.deepEqual(store.getState(), {
        loaded:     false,
        processing: false
      })
    })

    it("ignores unknown actions", () => {
      const initialState = { initial: "state" }
      const storeWithState = configureTestStore(
        makeReducer(fakeEndpoint, initialState)
      )
      assert.deepEqual(storeWithState.getState(), initialState)
    })
  })

  describe("makeAction", () => {
    let dispatchThen, fetchMock

    beforeEach(() => {
      dispatchThen = store.createDispatchThen()
      fetchMock = sinon.stub(api, "fetchJSONWithCSRF")
    })

    it("dispatches a success action if the API returned successfully", () => {
      const fetchAction = makeAction(fakeEndpoint)
      const params = {
        param1: "1",
        param2: "2"
      }
      fetchMock.returns(Promise.resolve("data"))

      return dispatchThen(fetchAction(params), [
        makeRequestActionType(fakeEndpoint.name),
        makeReceiveSuccessActionType(fakeEndpoint.name)
      ]).then(state => {
        assert.deepEqual(state, {
          data:        "data",
          processing:  false,
          loaded:      true,
          fetchStatus: FETCH_SUCCESS
        })

        sinon.assert.calledWith(fetchMock, "/api/v0/fake/", {
          method: "POST",
          body:   JSON.stringify(params)
        })
      })
    })

    it("dispatches a failure action if the API failed", async () => {
      const fetchAction = makeAction(fakeEndpoint)
      const action = dispatch =>
        fetchAction(params)(dispatch).catch(() => {
          // silence node.js warning about unhandled errors
        })
      const params = {
        param1: "1",
        param2: "2"
      }
      fetchMock.returns(Promise.reject("error"))

      const state = await dispatchThen(action, [
        makeRequestActionType(fakeEndpoint.name),
        makeReceiveFailureActionType(fakeEndpoint.name)
      ])

      assert.deepEqual(state, {
        error:       "error",
        processing:  false,
        loaded:      true,
        fetchStatus: FETCH_FAILURE
      })

      sinon.assert.calledWith(fetchMock, "/api/v0/fake/", {
        method: "POST",
        body:   JSON.stringify(params)
      })
    })
  })

  describe("endpoints", () => {
    it("include /api/v0/payment/", () => {
      const endpoint = endpoints.find(endpoint => endpoint.name === "payment")
      assert.equal(endpoint.url, "/api/v0/payment/")
      assert.deepEqual(
        endpoint.fetchOptions({ klassKey: 1, paymentAmount: "123" }),
        {
          method: "POST",
          body:   JSON.stringify({
            klass_key:      1,
            payment_amount: "123"
          })
        }
      )
    })
  })
})
