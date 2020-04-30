// @flow
import React from "react"
import { Provider } from "react-redux"
import { Route, Router as ReactRouter } from "react-router-dom"

import App from "./pages/App"
import withTracker from "./util/withTracker"

import type { Store } from "redux"

type Props = {
  store: Store<*, *>,
  history: Object,
  children: React$Element<*>
}

export default class Router extends React.Component<Props> {
  render() {
    const { children, history, store } = this.props

    return (
      <Provider store={store}>
        <ReactRouter history={history}>{children}</ReactRouter>
      </Provider>
    )
  }
}

export const routes = <Route url="/" component={withTracker(App)} />
