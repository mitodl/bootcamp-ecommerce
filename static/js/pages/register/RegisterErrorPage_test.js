// @flow
/* global SETTINGS: false */
import React from "react";
import { assert } from "chai";
import { shallow } from "enzyme";

import RegisterErrorPage from "./RegisterErrorPage";

describe("RegisterErrorPage", () => {
  const renderPage = () => shallow(<RegisterErrorPage />);

  it("displays a link to email support", async () => {
    const url = "https://test.edu/form";
    SETTINGS.support_url = url;
    const wrapper = await renderPage();

    assert.equal(wrapper.find("a").prop("href"), url);
  });
});
