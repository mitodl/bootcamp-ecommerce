// @flow
import React from "react"
import { Route } from "react-router"

import PaymentPage from "./PaymentPage"

import type { Match } from "react-router"

export default class App extends React.Component<*, void> {
  props: {
    match: Match
  }

  render() {
    const { match } = this.props

    return (
      <div className="app">
        <Route path={`${match.url}pay/`} component={PaymentPage} />
      </div>
    )
  }
}
