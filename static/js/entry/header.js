// @flow
/* global SETTINGS: false */
import { createBrowserHistory } from "history";
import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Provider as ReduxQueryProvider } from "redux-query-react";
import { Router as ReactRouter } from "react-router";
import { AppContainer } from "react-hot-loader";

import configureStore from "../store/configureStore";
import { AppTypeContext, MIXED_APP_CONTEXT } from "../contextDefinitions";
import { getQueries } from "../lib/redux_query";
import HeaderApp from "../pages/HeaderApp";

const store = configureStore();

const rootEl = document.getElementById("header");
if (!rootEl) {
  throw new Error("Unable to find 'header' element");
}

const renderHeader = () => {
  const history = createBrowserHistory();
  ReactDOM.render(
    <AppContainer>
      <Provider store={store}>
        <ReduxQueryProvider queriesSelector={getQueries}>
          <ReactRouter history={history}>
            <AppTypeContext.Provider value={MIXED_APP_CONTEXT}>
              <HeaderApp />
            </AppTypeContext.Provider>
          </ReactRouter>
        </ReduxQueryProvider>
      </Provider>
    </AppContainer>,
    rootEl,
  );
};

renderHeader();
