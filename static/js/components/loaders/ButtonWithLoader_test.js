// @flow
import React from "react"
import { shallow } from "enzyme"
import { assert } from "chai"

import ButtonWithLoader from "./ButtonWithLoader"
import { shouldIf } from "../../lib/test_utils"

describe("ButtonWithLoader", () => {
  it("renders a button with props", () => {
    const wrapper = shallow(
      <ButtonWithLoader
        loading={false}
        className="first-class second-class"
        aria-hidden={true}
      >
        buttontext
      </ButtonWithLoader>
    )
    assert.isTrue(wrapper.find("button").prop("aria-hidden"))
    assert.isFalse(wrapper.find("button").prop("disabled"))
    assert.equal(
      wrapper.find("button").prop("className"),
      "first-class second-class button-with-loader"
    )
    assert.equal(wrapper.find("button").text(), "buttontext")
  })

  it("renders a disabled button while loading", () => {
    const wrapper = shallow(<ButtonWithLoader loading={true} />)
    assert.isTrue(wrapper.find("button").prop("disabled"))
    assert.equal(wrapper.find("button").prop("className"), "button-with-loader")
    assert.isTrue(
      wrapper
        .find("button")
        .find("Spinner")
        .exists()
    )
  })

  describe("disabled", () => {
    [
      [undefined, true, true],
      [undefined, false, false],
      [true, true, true],
      [true, false, true],
      [false, true, false],
      [false, false, false]
    ].forEach(([disabled, loading, expectedDisabled]) => {
      it(`${shouldIf(expectedDisabled)} be disabled if disabled is ${String(
        disabled
      )} and loading is ${String(loading)}`, () => {
        const wrapper = shallow(
          <ButtonWithLoader loading={loading} disabled={disabled} />
        )
        assert.equal(wrapper.prop("disabled"), expectedDisabled)
      })
    })
  })
})
