import configureTestStore from 'redux-asserts';
import sinon from 'sinon';

import {
  setKlassId,
  setTotal,
} from '../actions';
import rootReducer from '../reducers';
import { createAssertReducerResultState } from '../util/test_utils';


describe('reducers', () => {
  let sandbox, store, assertReducerResultState;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    store = configureTestStore(rootReducer);
    assertReducerResultState = createAssertReducerResultState(store, state => state.ui);
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe('ui', () => {
    it('should set the total price', () => {
      assertReducerResultState(setTotal, ui => ui.total, '');
    });

    it('should set the klass id', () => {
      assertReducerResultState(setKlassId, ui => ui.klassId, '');
    });
  });

});
