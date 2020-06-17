// @flow
import React from "react"
import { shallow } from "enzyme"
import { assert } from "chai"

import Address from "./Address"

import { makeApplicationDetail } from "../factories/application"
import { makeCountries } from "../factories/user"

describe("Address", () => {
  let application, countries

  beforeEach(() => {
    application = makeApplicationDetail()
    countries = makeCountries()
  })

  it("renders the address", () => {
    application.user.legal_address = {
      ...application.user.legal_address,
      street_address:     ["123 Fake St", "Apartment 45"],
      city:               "Cambridge",
      state_or_territory: "US-MA",
      country:            "US",
      postal_code:        "99999"
    }
    const wrapper = shallow(
      <Address application={application} countries={countries} />
    )
    assert.equal(
      wrapper.text().trim(),
      "123 Fake StApartment 45Cambridge, MA 99999United States"
    )
  })

  it("renders an address even if pieces are missing", () => {
    // $FlowFixMe
    application.user.legal_address = {}
    const wrapper = shallow(
      <Address application={application} countries={countries} />
    )
    assert.equal(wrapper.text().trim(), "")
  })
})
