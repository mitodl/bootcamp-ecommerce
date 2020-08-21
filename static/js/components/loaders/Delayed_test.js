// @flow
import React from "react"
import { shallow } from "enzyme"
import wait from "waait"
import { assert } from "chai"

import Delayed from "./Delayed"

describe("Delayed", () => {
  it("delays for a period of time before rendering children", async () => {
    const inner = <span className="inner">inner contents</span>
    const wrapper = await shallow(<Delayed delay={10}>{inner}</Delayed>)
    assert.isFalse(wrapper.find(".inner").exists())
    await wait(20)
    assert.isTrue(wrapper.find(".inner").exists())
    assert.equal(wrapper.find(".inner").text(), "inner contents")
  })
})
