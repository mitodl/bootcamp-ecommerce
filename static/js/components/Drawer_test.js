// @flow
import React from "react"
import { assert } from "chai"
import { Drawer as RMWCDrawer } from "@rmwc/drawer"

import Drawer from "./Drawer"

import IntegrationTestHelper from "../util/integration_test_helper"
import { toggleDrawer } from "../reducers/drawer"

describe("Drawer", () => {
  let helper, render

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    render = helper.configureReduxQueryRenderer(Drawer)
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("should render a drawer component with children", async () => {
    const { wrapper } = await render(
      {
        children: <div className="testtesttest">test</div>
      },
      [toggleDrawer()]
    )
    assert.ok(wrapper.find(RMWCDrawer).exists())
    assert.equal(wrapper.find(".testtesttest").text(), "test")
  })

  it("should have the drawer open if action is dispatch", async () => {
    const { wrapper } = await render({}, [toggleDrawer()])
    assert.isTrue(wrapper.find(RMWCDrawer).prop("open"))
  })

  it("should pass down a close function to drawer", async () => {
    const { wrapper, store } = await render({}, [toggleDrawer()])
    wrapper.find(RMWCDrawer).prop("onClose")()
    assert.isFalse(store.getState().drawer.showDrawer)
  })
})
