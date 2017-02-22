require('react-hot-loader/patch');
/* global SETTINGS:false */
__webpack_public_path__ = `${SETTINGS.public_path}`;  // eslint-disable-line no-undef, camelcase
import React from 'react';
import ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';

import configureStore from '../store/configureStore';
import ga from 'react-ga';
import Root from '../Root';

// Object.entries polyfill
import entries from 'object.entries';
if (!Object.entries) {
  entries.shim();
}

const store = configureStore();

let debug = SETTINGS.reactGaDebug === "true";
if (SETTINGS.gaTrackingID) {
  ga.initialize(SETTINGS.gaTrackingID, { debug: debug });
}

const rootEl = document.getElementById("container");
const renderApp = Component => {
  ReactDOM.render(
    <AppContainer>
      <Component store={store} />
    </AppContainer>,
    rootEl
  );
};

renderApp(Root);

if (module.hot) {
  module.hot.accept('../Root', () => {
    const RootNext = require('../Root').default;
    renderApp(RootNext);
  });
}
