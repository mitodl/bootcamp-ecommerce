import React from 'react';
import { Route, Router } from 'react-router';
import { Provider } from 'react-redux';

import App from './containers/App';

/**
 * Create the routes (the root React elements to be rendered into our div)
 *
 * @param browserHistory A browserHistory object
 * @param store The redux store to be used
 * @param onRouteUpdate {function} Function called when the route changes
 * @returns {ReactElement}
 */
export function makeRoutes(browserHistory, store, onRouteUpdate) {
  return <div>
    <Provider store={store}>
      <Router history={browserHistory} onUpdate={onRouteUpdate}>
        <Route path="/" component={App} />
      </Router>
    </Provider>
  </div>;
}
