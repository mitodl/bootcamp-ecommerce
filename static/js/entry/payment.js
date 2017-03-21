// @flow
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import configureStore from '../store/configureStore';
import Payment from '../containers/Payment';

const store = configureStore();

const rootEl = document.getElementById("pay");
ReactDOM.render(
  <Provider store={store}>
    <Payment />
  </Provider>,
  rootEl,
);
