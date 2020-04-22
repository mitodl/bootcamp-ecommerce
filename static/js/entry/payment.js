// @flow
import {createBrowserHistory} from "history"
import React from "react"
import ReactDOM from "react-dom"
import { AppContainer } from "react-hot-loader"

import configureStore from "../store/configureStore"
import Router, { routes } from "../Router"

const store = configureStore()

const rootEl = document.getElementById("container")
if (!rootEl) {
  throw new Error("Unable to find 'container' element")
}

const renderApp = Component => {
  const history = createBrowserHistory()
  ReactDOM.render(
    <AppContainer>
      <Component history={history} store={store}>
        {routes}
      </Component>
    </AppContainer>,
    rootEl
  )
}

renderApp(Router)
