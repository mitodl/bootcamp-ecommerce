// @flow
import { assert } from "chai";

import { makeUser } from "../factories/user";
import UserDetails from "./UserDetails";
import React from "react";
import { shallow } from "enzyme";

describe("UserDetails", () => {
  const user = makeUser();
  const renderDisplay = () => shallow(<UserDetails user={user} />);

  it("renders UserDetails for a user", async () => {
    const wrapper = renderDisplay();
    assert.isTrue(
      wrapper
        .text()
        // $FlowFixMe: user.legal_address is not null
        .includes(user.legal_address.street_address[0]),
    );
    assert.isTrue(
      wrapper
        .text()
        // $FlowFixMe: user.profile is not null
        .includes(user.profile.company),
    );
  });
});
