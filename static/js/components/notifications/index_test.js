// @flow
import React from "react";
import { assert } from "chai";
import { shallow } from "enzyme";

import { TextNotification } from ".";
import IntegrationTestHelper from "../../util/integration_test_helper";

describe("Notification component", () => {
  let helper, dismissStub;

  beforeEach(() => {
    helper = new IntegrationTestHelper();
    dismissStub = helper.sandbox.stub();
  });

  afterEach(() => {
    helper.cleanup();
  });

  it("TextNotification", () => {
    const text = "Some text";
    const wrapper = shallow(
      <TextNotification text={"Some text"} dismiss={dismissStub} />,
    );
    assert.equal(wrapper.text(), text);
  });
});
