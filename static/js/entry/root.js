// @flow
/* global SETTINGS: false */
import { createBrowserHistory } from "history";
import React from "react";
import ReactDOM from "react-dom";
import { AppContainer } from "react-hot-loader";

import configureStore from "../store/configureStore";
import Router, { routes } from "../Router";
import NotificationContainer from "../components/notifications/NotificationContainer";
import { ALERT_TYPE_ERROR, ALERT_TYPE_SUCCESS } from "../constants";
import { AppTypeContext, SPA_APP_CONTEXT } from "../contextDefinitions";

// Zendesk react module
import Zendesk from "react-zendesk";
import { Provider } from "react-redux";

const ZENDESK_KEY = SETTINGS.zendesk_config.help_widget_key;
const ZENDESK_ENABLED = SETTINGS.zendesk_config.help_widget_enabled;

const loadZendesk = () => {
  return <Zendesk zendeskKey={ZENDESK_KEY} />;
};

const renderApp = (component, selector) => {
  const element = document.querySelector(selector);
  if (!element) {
    throw new Error(`Unable to find element for selector ${selector}`);
  }
  if (ZENDESK_ENABLED && ZENDESK_KEY) {
    loadZendesk();
  }
  ReactDOM.render(
    <AppContainer>
      <AppTypeContext.Provider value={SPA_APP_CONTEXT}>
        {component}
      </AppTypeContext.Provider>
    </AppContainer>,
    element,
  );
};

const store = configureStore();

renderApp(
  <Router history={createBrowserHistory()} store={store}>
    {routes}
  </Router>,
  "#app-container",
);
renderApp(
  <Provider store={store}>
    <NotificationContainer
      alertTypes={[ALERT_TYPE_SUCCESS, ALERT_TYPE_ERROR]}
    />
  </Provider>,
  "#footer-notifications",
);
