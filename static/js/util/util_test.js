import { assert } from 'chai';

import { generateFakeKlasses } from '../factories';
import {
  createForm,
  isNilOrBlank,
  formatDollarAmount,
  getKlassWithFulfilledOrder,
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

  describe('getKlassWithFulfilledOrder', () => {
    it('gets a fulfilled order from the payments in the klasses', () => {
      const klasses = generateFakeKlasses(1, true);
      const klass = klasses[0];
      assert.deepEqual(
        getKlassWithFulfilledOrder(klasses, klass.payments[0].order.id),
        klass,
      );
    });

    it("returns undefined if the order doesn't exist", () => {
      const klasses = generateFakeKlasses(1);
      assert.deepEqual(
        getKlassWithFulfilledOrder(klasses, 3),
        undefined,
      );
    });

    it("returns undefined if the order is not fulfilled", () => {
      const klasses = generateFakeKlasses(1, true);
      const klass = klasses[0];
      klass.payments[0].order.status = 'created';
      assert.deepEqual(
        getKlassWithFulfilledOrder(klasses, klass.payments[0].order.id),
        undefined,
      );
    });
  });
});
