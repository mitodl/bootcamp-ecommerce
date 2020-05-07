// @flow
import React from "react"
import { Provider } from "react-redux"
import { Route, Router as ReactRouter } from "react-router-dom"
import { Provider as ReduxQueryProvider } from "redux-query-react"

import ScrollToTop from "./components/ScrollToTop"
import App from "./pages/App"
import withTracker from "./util/withTracker"

import { getQueries } from "./lib/redux_query"

import type { Store } from "redux"

type Props = {
  store: Store<*, *>,
  history: Object,
  children: React$Element<*>
}

export default function Router(props: Props) {
  const { children, history, store } = props

  return (
    <Provider store={store}>
      <ReduxQueryProvider queriesSelector={getQueries}>
        <ReactRouter history={history}>
          <ScrollToTop>{children}</ScrollToTop>
        </ReactRouter>
      </ReduxQueryProvider>
    </Provider>
  )
}

export const routes = <Route url="/" component={withTracker(App)} />
