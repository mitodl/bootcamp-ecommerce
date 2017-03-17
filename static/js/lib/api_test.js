// @flow
import sinon from 'sinon';
import { assert } from 'chai';

import * as apiUtil from './api_util';
import { sendPayment } from './api';

describe('REST functions', () => {
  let sandbox, fetchJSONStub;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    fetchJSONStub = sandbox.stub(apiUtil, 'fetchJSONWithCSRF');
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe('sendPayment', () => {
    it('sends payment total successfully', () => {
      fetchJSONStub.returns(Promise.resolve());

      let total = 'total';
      return sendPayment(total).then(() => {
        assert.ok(fetchJSONStub.calledWith('/api/v0/payment/', {
          method: 'POST',
          body: JSON.stringify({
            total: total
          })
        }));
      });
    });

    it('fails to send payment total', () => {
      fetchJSONStub.returns(Promise.reject());

      let total = 'total';
      return assert.isRejected(sendPayment(total)).then(() => {
        assert.ok(fetchJSONStub.calledWith('/api/v0/payment/', {
          method: 'POST',
          body: JSON.stringify({
            total: total
          })
        }));
      });
    });
  });
});

