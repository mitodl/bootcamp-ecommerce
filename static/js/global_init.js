// Define globals we would usually get from Django
const _createSettings = () => ({
  full_name: 'Jane Doe',
});

global.SETTINGS = _createSettings();

// polyfill for Object.entries
import entries from 'object.entries';
if (!Object.entries) {
  entries.shim();
}

require('jsdom-global')();

afterEach(() => { // eslint-disable-line mocha/no-top-level-hooks
  document.body.innerHTML = '';
  global.SETTINGS = _createSettings();
});

// enable chai-as-promised
import chai from 'chai';
import chaiAsPromised from 'chai-as-promised';
chai.use(chaiAsPromised);
