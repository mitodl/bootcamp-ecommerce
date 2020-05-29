// @flow
/* global SETTINGS: false */
import { createBrowserHistory } from "history"
import React from "react"
import ReactDOM from "react-dom"
import { AppContainer } from "react-hot-loader"
import "../notifications.js"

import configureStore from "../store/configureStore"
import Router, { routes } from "../Router"

// Zendesk react module
import Zendesk from "react-zendesk"

const ZENDESK_KEY = SETTINGS.zendesk_config.help_widget_key
const ZENDESK_ENABLED = SETTINGS.zendesk_config.help_widget_enabled

const store = configureStore()

const rootEl = document.getElementById("container")
if (!rootEl) {
  throw new Error("Unable to find 'container' element")
}

const loadZendesk = () => {
  return <Zendesk zendeskKey={ZENDESK_KEY} />
}

const renderApp = Component => {
  const history = createBrowserHistory()
  if (ZENDESK_ENABLED && ZENDESK_KEY) {
    loadZendesk()
  }
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
