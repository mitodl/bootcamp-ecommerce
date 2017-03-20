import { createAction } from 'redux-actions';
import sinon from 'sinon';
import configureTestStore from 'redux-asserts';
import { assert } from 'chai';

import * as api from './lib/api';
import {
  FETCH_PROCESSING,
  FETCH_SUCCESS,
  FETCH_FAILURE,
} from './actions';
import {
  endpoints,
  makeAction,
  makeReducer,
  makeRequestActionType,
  makeReceiveSuccessActionType,
  makeReceiveFailureActionType,
  makeClearType,
} from './rest';

describe('rest', () => {
  const fakeEndpoint = {
    name: 'fake',
    url: '/api/v0/fake/',
    makeOptions: (...args) => ({
      method: 'POST',
      body: JSON.stringify([...args])
    }),
  };

  let sandbox, store;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    store = configureTestStore(makeReducer(fakeEndpoint));
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe('makeReducer', () => {
    it('has an initial state', () => {
      let initialState = {initial: "state"};
      const storeWithState = configureTestStore(makeReducer(fakeEndpoint, initialState));
      assert.deepEqual(storeWithState.getState(), initialState);
    });

    it('handles a request action', () => {
      store.dispatch(createAction(makeRequestActionType(fakeEndpoint.name))());
      assert.deepEqual(store.getState(), {
        fetchStatus: FETCH_PROCESSING,
        loaded: false,
        processing: true,
      });
    });

    it('handles a receive success action', () => {
      store.dispatch(createAction(makeReceiveSuccessActionType(fakeEndpoint.name))("data"));
      assert.deepEqual(store.getState(), {
        fetchStatus: FETCH_SUCCESS,
        loaded: true,
        processing: false,
        data: "data",
      });
    });

    it('handles a receive failure action', () => {
      store.dispatch(createAction(makeReceiveFailureActionType(fakeEndpoint.name))("error"));
      assert.deepEqual(store.getState(), {
        fetchStatus: FETCH_FAILURE,
        loaded: true,
        processing: false,
        error: "error",
      });
    });

    it('handles a clear action', () => {
      store.dispatch(createAction(makeRequestActionType(fakeEndpoint.name))());
      store.dispatch(createAction(makeClearType(fakeEndpoint.name))());
      assert.deepEqual(store.getState(), {
        loaded: false,
        processing: false,
      });
    });

    it('ignores unknown actions', () => {
      const initialState = {initial: "state"};
      const storeWithState = configureTestStore(makeReducer(fakeEndpoint, initialState));
      assert.deepEqual(storeWithState.getState(), initialState);
    });
  });

  describe('makeAction', () => {
    let dispatchThen, fetchMock;

    beforeEach(() => {
      dispatchThen = store.createDispatchThen();
      fetchMock = sandbox.stub(api, 'fetchJSONWithCSRF');
    });

    it('dispatches a success action if the API returned successfully', () => {
      const fetchAction = makeAction(fakeEndpoint);
      const args = ["arg1", "arg2"];
      fetchMock.returns(Promise.resolve("data"));

      return dispatchThen(fetchAction(...args), [
        makeRequestActionType(fakeEndpoint.name),
        makeReceiveSuccessActionType(fakeEndpoint.name),
      ]).then(state => {
        assert.deepEqual(state, {
          data: "data",
          processing: false,
          loaded: true,
          fetchStatus: FETCH_SUCCESS,
        });

        sinon.assert.calledWith(fetchMock, '/api/v0/fake/', {
          method: "POST",
          body: JSON.stringify(args),
        });
      });
    });

    it('dispatches a failure action if the API failed', () => {
      const fetchAction = makeAction(fakeEndpoint);
      const args = ["arg1", "arg2"];
      fetchMock.returns(Promise.reject("error"));

      return dispatchThen(fetchAction(...args), [
        makeRequestActionType(fakeEndpoint.name),
        makeReceiveFailureActionType(fakeEndpoint.name),
      ]).then(state => {
        assert.deepEqual(state, {
          error: "error",
          processing: false,
          loaded: true,
          fetchStatus: FETCH_FAILURE,
        });

        sinon.assert.calledWith(fetchMock, '/api/v0/fake/', {
          method: "POST",
          body: JSON.stringify(args),
        });
      });
    });
  });

  describe("endpoints", () => {
    it('has /api/v0/payment/', () => {
      let endpoint = endpoints.find(endpoint => endpoint.name === 'payment');
      assert.equal(endpoint.url, '/api/v0/payment/');
      assert.deepEqual(endpoint.makeOptions("123"), {
        method: 'POST',
        body: JSON.stringify({
          total: "123"
        })
      });
    });
  });
});
