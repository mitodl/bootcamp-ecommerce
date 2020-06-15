// @flow
import { assert } from "chai"
import { Drawer as RMWCDrawer } from "@rmwc/drawer"

import Drawer from "./Drawer"
import {
  NEW_APPLICATION,
  PAYMENT,
  PROFILE_EDIT,
  PROFILE_VIEW
} from "../constants"

import IntegrationTestHelper from "../util/integration_test_helper"
import { setDrawerOpen, setDrawerState, openDrawer } from "../reducers/drawer"
import { makeApplicationDetail } from "../factories/application"

describe("Drawer", () => {
  let helper, render

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    // Mock API response for bootcamp runs. NewApplication requests this when loading
    helper.handleRequestStub
      .withArgs("/api/bootcampruns/?available=true")
      .returns({
        status: 200,
        body:   []
      })
    render = helper.configureReduxQueryRenderer(Drawer)
  })

  afterEach(() => {
    helper.cleanup()
  })

  //
  ;[
    [PROFILE_EDIT, "EditProfileDisplay"],
    [PROFILE_VIEW, "ViewProfileDisplay"],
    [PAYMENT, "PaymentDisplay"],
    [NEW_APPLICATION, "NewApplication"]
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

  it("should have the drawer open if action is dispatched", async () => {
    const { wrapper } = await render({}, [setDrawerOpen(true)])
    assert.isTrue(wrapper.find(RMWCDrawer).prop("open"))
  })

  it("should pass down a close function to drawer", async () => {
    const { wrapper, store } = await render({}, [setDrawerOpen(false)])
    wrapper.find(RMWCDrawer).prop("onClose")()
    assert.isFalse(store.getState().drawer.drawerOpen)
  })

  it("should pass down metadata to an inner drawer component (if metadata exists)", async () => {
    const meta = { application: makeApplicationDetail() }
    const { wrapper, store } = await render({}, [
      openDrawer({ type: PAYMENT, meta: meta })
    ])
    assert.isTrue(wrapper.find(RMWCDrawer).prop("open"))
    assert.deepEqual(store.getState().drawer.drawerMeta, meta)
    Object.keys(meta).forEach((key: string) => {
      assert.deepEqual(wrapper.find("PaymentDisplay").prop(key), meta[key])
    })
  })
})
