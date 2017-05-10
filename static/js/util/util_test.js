import { assert } from 'chai';

import {
  createForm,
  isNilOrBlank,
  formatDollarAmount
} from './util';

describe('util', () => {
  describe('createForm', () => {
    it('creates a form with hidden values corresponding to the payload', () => {
      const url = 'url';
      const payload = {'pay': 'load'};
      const form = createForm(url, payload);

      let clone = {...payload};
      for (let hidden of form.querySelectorAll("input[type=hidden]")) {
        const key = hidden.getAttribute('name');
        const value = hidden.getAttribute('value');
        assert.equal(clone[key], value);
        delete clone[key];
      }
      // all keys exhausted
      assert.deepEqual(clone, {});
      assert.equal(form.getAttribute("action"), url);
      assert.equal(form.getAttribute("method"), "post");
    });
  });

  describe('isNilOrBlank', () => {
    it('returns true for undefined, null, and a blank string', () => {
      [undefined, null, ''].forEach(value => {
        assert.isTrue(isNilOrBlank(value));
      });
    });

    it('returns false for a non-blank string', () => {
      assert.isFalse(isNilOrBlank('not blank'));
    });
  });

  describe('formatDollarAmount', () => {
    it('returns a properly formatted dollar value', () => {
      [undefined, null].forEach((nilValue) => {
        assert.equal(formatDollarAmount(nilValue), '$0');
      });
      assert.equal(formatDollarAmount(100), '$100');
      assert.equal(formatDollarAmount(10000), '$10,000');
      assert.equal(formatDollarAmount(100.12), '$100.12');
    });
  });
});
