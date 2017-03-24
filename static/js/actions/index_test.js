import { assertCreatedActionHelper } from './test_util';

import {
  setKlassId,
  setTotal,

  SET_KLASS_ID,
  SET_TOTAL,
} from './index';

describe('actions', () => {
  it('should create all action creators', () => {
    [
      [setTotal, SET_TOTAL],
      [setKlassId, SET_KLASS_ID],
    ].forEach(assertCreatedActionHelper);
  });
});
