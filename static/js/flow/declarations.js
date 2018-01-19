// @flow
declare var SETTINGS: {
  user: {
    full_name: string,
    username: string
  },
  facebook_pixel_id: string
};

// mocha
declare var it: Function;
declare var beforeEach: Function;
declare var afterEach: Function;
declare var describe: Function;

// webpack
declare var __webpack_public_path__: string; // eslint-disable-line camelcase
