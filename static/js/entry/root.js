require('react-hot-loader/patch');
/* global SETTINGS:false */
__webpack_public_path__ = `${SETTINGS.public_path}`;  // eslint-disable-line no-undef, camelcase

// Object.entries polyfill
import entries from 'object.entries';
if (!Object.entries) {
  entries.shim();
}
