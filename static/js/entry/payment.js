// @flow
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import configureStore from '../store/configureStore';
import PaymentPage from '../containers/PaymentPage';

const store = configureStore();

const rootEl = document.getElementById("pay");
ReactDOM.render(
  <Provider store={store}>
    <PaymentPage />
  </Provider>,
  rootEl,
);
