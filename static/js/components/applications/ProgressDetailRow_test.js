// @flow
import React from "react";
import { shallow } from "enzyme";
import { assert } from "chai";

import ProgressDetailRow from "./ProgressDetailRow";
import { shouldIf } from "../../lib/test_utils";

describe("ProgressDetailRow", () => {
  const className = "some-class",
    contents = <p>contents...</p>,
    defaultProps = {
      className: className,
      fulfilled: true,
    };

  const render = (props) =>
    shallow(
      <ProgressDetailRow {...defaultProps} {...props}>
        {contents}
      </ProgressDetailRow>,
    );

  it("renders children", () => {
    const wrapper = render();
    const contentsWrapper = wrapper.find(".detail-content .row");
    assert.equal(contentsWrapper.childAt(0).type(), contents.type);
    assert.equal(contentsWrapper.text(), contents.props.children);
  });

  it("add CSS classes to the top level HTML element", () => {
    let wrapper = render();
    let detailSection = wrapper.find(".detail-section");
    assert.equal(
      detailSection.prop("className"),
      `detail-section ${className} fulfilled`,
    );

    wrapper = render({ fulfilled: false });
    detailSection = wrapper.find(".detail-section");
    assert.equal(
      detailSection.prop("className"),
      `detail-section ${className}`,
    );
  });

  //
  [false, true].forEach((fulfilled) => {
    it(`${shouldIf(
      fulfilled,
    )} show a checkmark if the 'fulfilled' prop === ${String(
      fulfilled,
    )}`, () => {
      const wrapper = render({ fulfilled: fulfilled });
      const detailSection = wrapper.find(".detail-section");
      const assertFn = fulfilled ? assert.include : assert.notInclude;
      assertFn(detailSection.prop("className"), " fulfilled");
      const checkmark = detailSection.find(".check i.material-icons");
      assert.equal(checkmark.exists(), fulfilled);
    });
  });
});
