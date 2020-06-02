// @flow
import { assert } from "chai"
import { Drawer as RMWCDrawer } from "@rmwc/drawer"

import Drawer from "./Drawer"
import { PAYMENT, PROFILE_EDIT, PROFILE_VIEW } from "../constants"

import IntegrationTestHelper from "../util/integration_test_helper"
import {
  setDrawerOpen,
  setDrawerState,
  setDrawerMeta
} from "../reducers/drawer"

describe("Drawer", () => {
  let helper, render

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    render = helper.configureReduxQueryRenderer(Drawer)
  })

  afterEach(() => {
    helper.cleanup()
  })

  //
  ;[
    [PROFILE_EDIT, "EditProfileDisplay"],
    [PROFILE_VIEW, "ViewProfileDisplay"],
    [PAYMENT, "PaymentDisplay"]
  ].forEach(([drawerType, expComponent]) => {
    it(`should render a drawer component with a ${expComponent} child`, async () => {
      const { wrapper } = await render({}, [
        setDrawerState(drawerType),
        setDrawerOpen(true)
      ])
      assert.ok(wrapper.find(RMWCDrawer).exists())
      assert.isTrue(wrapper.find(expComponent).exists())
    })
  })

  it("should have the drawer open if action is dispatch", async () => {
    const { wrapper } = await render({}, [setDrawerOpen(true)])
    assert.isTrue(wrapper.find(RMWCDrawer).prop("open"))
  })

  it("should pass down a close function to drawer", async () => {
    const { wrapper, store } = await render({}, [setDrawerOpen(false)])
    wrapper.find(RMWCDrawer).prop("onClose")()
    assert.isFalse(store.getState().drawer.drawerOpen)
  })

  it("should set metadata for drawer", async () => {
    const data = { meta: "data" }
    const { store } = await render({}, [setDrawerMeta(data)])
    assert.deepEqual(store.getState().drawer.drawerMeta, data)
  })
})
