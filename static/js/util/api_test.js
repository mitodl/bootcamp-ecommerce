import assert from 'assert';
import fetchMock  from 'fetch-mock/src/server';
import sinon from 'sinon';

import {
  patchThing,
  getCookie,
  fetchJSONWithCSRF,
  csrfSafeMethod,
} from './api';
import * as api from './api';
import { THING_RESPONSE } from '../constants';

describe('api', () => {
  let sandbox;
  let savedWindowLocation;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    savedWindowLocation = null;
    Object.defineProperty(window, "location", {
      set: value => {
        savedWindowLocation = value;
      }
    });
  });
  afterEach(function() {
    sandbox.restore();
    fetchMock.restore();

    for (let cookie of document.cookie.split(";")) {
      let key = cookie.split("=")[0].trim();
      document.cookie = `${key}=`;
    }
  });

  describe('REST functions', () => {
    let fetchStub;
    beforeEach(() => {
      fetchStub = sandbox.stub(api, 'fetchJSONWithCSRF');
    });

    it('patches a thing', done => {
      fetchStub.returns(Promise.resolve(THING_RESPONSE));

      patchThing('jane', THING_RESPONSE).then(thing => {
        assert.ok(fetchStub.calledWith('/api/v0/thing/jane/', {
          method: 'PATCH',
          body: JSON.stringify(THING_RESPONSE)
        }));
        assert.deepEqual(thing, THING_RESPONSE);
        done();
      });
    });

    it('fails to patch a thing', done => {
      fetchStub.returns(Promise.reject());
      patchThing('jane', THING_RESPONSE).catch(() => {
        assert.ok(fetchStub.calledWith('/api/v0/thing/jane/', {
          method: 'PATCH',
          body: JSON.stringify(THING_RESPONSE)
        }));
        done();
      });
    });
  });
  describe('fetchJSONWithCSRF', () => {
    it('fetches and populates appropriate headers for JSON', done => {
      document.cookie = "csrftoken=asdf";
      let expectedJSON = { data: true };

      fetchMock.mock('/url', (url, opts) => {
        assert.deepEqual(opts, {
          credentials: "same-origin",
          headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": "asdf"
          },
          body: JSON.stringify(expectedJSON),
          method: "PATCH"
        });
        return {status: 200};
      });

      fetchJSONWithCSRF('/url', {
        method: 'PATCH',
        body: JSON.stringify(expectedJSON)
      }).then(() => {
        done();
      });
    });

    for (let statusCode of [199, 300, 400, 500, 100]) {
      it(`rejects the promise if the status code is ${statusCode}`, done => {
        fetchMock.mock('/url', () => {
          return { status: statusCode };
        });

        fetchJSONWithCSRF('/url').catch(() => {
          done();
        });
      });
    }

    for (let statusCode of [400, 401]) {
      it(`redirects to login if we set loginOnError and status = ${statusCode}`, done => {
        fetchMock.mock('/url', () => {
          return {status: 400};
        });

        fetchJSONWithCSRF('/url', {}, true).catch(() => {
          assert.equal(savedWindowLocation, '/login/edxorg/');
          done();
        });
      });
    }
  });

  describe('getCookie', () => {
    it('gets a cookie', () => {
      document.cookie = 'key=cookie';
      assert.equal('cookie', getCookie('key'));
    });

    it('handles multiple cookies correctly', () => {
      document.cookie = 'key1=cookie1';
      document.cookie = 'key2=cookie2';
      assert.equal('cookie1', getCookie('key1'));
      assert.equal('cookie2', getCookie('key2'));
    });
    it('returns null if cookie not found', () => {
      assert.equal(null, getCookie('unknown'));
    });
  });

  describe('csrfSafeMethod', () => {
    it('knows safe methods', () => {
      for (let method of ['GET', 'HEAD', 'OPTIONS', 'TRACE']) {
        assert.ok(csrfSafeMethod(method));
      }
    });
    it('knows unsafe methods', () => {
      for (let method of ['PATCH', 'PUT', 'DELETE', 'POST']) {
        assert.ok(!csrfSafeMethod(method));
      }
    });
  });
});