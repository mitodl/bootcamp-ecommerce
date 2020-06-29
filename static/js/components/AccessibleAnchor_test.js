import React from "react"
import { shallow } from "enzyme"
import { assert } from "chai"
import sinon from "sinon"

import AccessibleAnchor from "./AccessibleAnchor"

describe("AccessibleAnchor", () => {
  const render = (props = {}) => shallow(<AccessibleAnchor {...props} />)

  it("should render children", () => {
    assert.equal("children", render({ children: "children" }).prop("children"))
  })

  it("should have a tabindex", () => {
    assert.equal(render().prop("tabIndex"), "0")
  })

  it("should set a className", () => {
    assert.ok(
      render({ className: "my-class-name" })
        .find(".my-class-name")
        .exists()
    )
  })

  it("should set an onclick handler", () => {
    const onClick = sinon.stub()
    render({ onClick }).simulate("click")
    sinon.assert.called(onClick)
  })

  it("should allow keyboard triggering of onclick handler", () => {
    const onClick = sinon.stub()
    render({ onClick }).simulate("keypress", { key: "Enter" })
    sinon.assert.called(onClick)
  })
})
