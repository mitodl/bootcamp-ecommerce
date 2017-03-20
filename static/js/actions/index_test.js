import { assertCreatedActionHelper } from './test_util';

import {
  setTotal,

  SET_TOTAL,
} from './index';

describe('actions', () => {
  it('should create all action creators', () => {
    [
      [setTotal, SET_TOTAL],
    ].forEach(assertCreatedActionHelper);
  });
});
