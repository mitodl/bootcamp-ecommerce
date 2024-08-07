// @flow
declare var SETTINGS: {
  gaTrackingID: string,
  reactGaDebug: boolean,
  recaptchaKey: ?string,
  upload_max_size: number,
  support_url: string,
  terms_url: string,
  novoed_base_url: string,
  zendesk_config: {
    help_widget_enabled: boolean,
    help_widget_key: ?string,
  },
};

// mocha
declare var it: Function;
declare var beforeEach: Function;
declare var afterEach: Function;
declare var describe: Function;

// webpack
declare var __webpack_public_path__: string; // eslint-disable-line camelcase
