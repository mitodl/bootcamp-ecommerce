// Define globals we would usually get from Django
const _createSettings = () => ({
  user: {
    username: "jane",
    email: "jane@example.com",
    first_name: "Jane",
    last_name: "Doe",
    preferred_name: "JD"
  },
  edx_base_url: "/edx/",
  support_email: "a_real_email@example.com"
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
