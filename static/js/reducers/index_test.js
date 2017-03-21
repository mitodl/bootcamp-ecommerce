import { assert } from 'chai';
import configureTestStore from 'redux-asserts';
import sinon from 'sinon';

import { setTotal } from '../actions';
import rootReducer from '../reducers';

describe('reducers', () => {
  let sandbox, store;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    store = configureTestStore(rootReducer);
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe('ui', () => {
    it('should set the total price', () => {
      assert.equal(store.getState().ui.total, '');
      store.dispatch(setTotal("price"));
      assert.equal(store.getState().ui.total, "price");
    });
  });

});
