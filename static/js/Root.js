// @flow
/* global SETTINGS: false */
import React from 'react';
import { Provider } from 'react-redux';
import type { Store } from 'redux';

import App from './containers/App';

export default class Root extends React.Component {
  props: {
    store:          Store,
  };

  render () {
    const { store } = this.props;

    return <div>
      <Provider store={store}>
        <App />
      </Provider>
    </div>;
  }
}
