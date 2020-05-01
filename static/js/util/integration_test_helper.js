/* global SETTINGS: false */
import React from "react"
import { Provider } from "react-redux"
import { Provider as ReduxQueryProvider } from "redux-query-react"
import { Router } from "react-router"
import R from "ramda"
import { mount, shallow } from "enzyme"
import sinon from "sinon"
import { createMemoryHistory } from "history"

import { getQueries } from "../lib/redux_query"
import * as storeLib from "../store/configureStore"
import * as networkInterfaceFuncs from "../store/network_interface"

import type { Sandbox } from "../flow/sinonTypes"

export default class IntegrationTestHelper {
  sandbox: Sandbox
  browserHistory: History
  actions: Array<any>

  constructor() {
    this.sandbox = sinon.createSandbox({})
    this.actions = []

    this.scrollIntoViewStub = this.sandbox.stub()
    window.HTMLDivElement.prototype.scrollIntoView = this.scrollIntoViewStub
    window.HTMLFieldSetElement.prototype.scrollIntoView = this.scrollIntoViewStub
    this.browserHistory = createMemoryHistory()
    this.currentLocation = null
    this.browserHistory.listen(url => {
      this.currentLocation = url
    })

    const defaultResponse = {
      body:   {},
      status: 200
    }
    this.handleRequestStub = this.sandbox.stub().returns(defaultResponse)
    this.sandbox
      .stub(networkInterfaceFuncs, "makeRequest")
      .callsFake((url, method, options) => ({
        execute: callback => {
          const response = this.handleRequestStub(url, method, options)
          const err = null
          const resStatus = (response && response.status) || 0
          const resBody = (response && response.body) || undefined
          const resText = (response && response.text) || undefined
          const resHeaders = (response && response.header) || undefined

          callback(err, resStatus, resBody, resText, resHeaders)
        },
        abort: () => {
          throw new Error("Aborts currently unhandled")
        }
      }))
  }

  cleanup() {
    this.actions = []
    this.sandbox.restore()
  }

  createFullStore(initialState) {
    return storeLib.default(initialState)
  }

  configureReduxQueryRenderer(Component, defaultProps = {}, initialStore = {}) {
    const history = this.browserHistory
    return async (extraProps = { history }, beforeRenderActions = []) => {
      const store = this.createFullStore(initialStore)
      beforeRenderActions.forEach(action => store.dispatch(action))

      const wrapper = await mount(
        <Provider store={store}>
          <ReduxQueryProvider queriesSelector={getQueries}>
            <Router store={store} history={this.browserHistory}>
              <Component {...defaultProps} {...extraProps} />
            </Router>
          </ReduxQueryProvider>
        </Provider>
      )
      this.wrapper = wrapper
      wrapper.update()
      return { wrapper, store }
    }
  }

  configureHOCRenderer(
    WrappedComponent: Class<React.Component<*, *>>,
    InnerComponent: Class<React.Component<*, *>>,
    defaultState: Object,
    defaultProps = {}
  ) {
    const history = this.browserHistory
    return async (extraState = {}, extraProps = {}) => {
      const initialState = R.mergeDeepRight(defaultState, extraState)
      const store = storeLib.default(initialState)
      const wrapper = await shallow(
        <WrappedComponent
          store={store}
          dispatch={store.dispatch}
          history={history}
          {...defaultProps}
          {...extraProps}
        />,
        {
          context: {
            // TODO: should be removed in the near future after upgrading enzyme
            store
          }
        }
      )

      // just a little convenience method
      store.getLastAction = function() {
        const actions = this.getActions()
        return actions[actions.length - 1]
      }

      // dive through layers of HOCs until we reach the desired inner component
      let inner = wrapper
      while (!inner.is(InnerComponent)) {
        // determine the type before we dive
        const cls = inner.type()
        if (InnerComponent === cls.WrappedComponent) {
          break
        }

        // shallow render this component
        inner = await inner.dive()

        // if it defines WrappedComponent, find() that so we skip over any intermediaries
        if (
          cls &&
          cls.hasOwnProperty("WrappedComponent") && // eslint-disable-line no-prototype-builtins
          inner.find(cls.WrappedComponent).length
        ) {
          inner = inner.find(cls.WrappedComponent)
        }
      }
      // one more time to shallow render the InnerComponent
      inner = await inner.dive()

      return { wrapper, inner, store }
    }
  }
}
