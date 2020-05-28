// @flow
import { assert } from "chai"

import ViewProfileDisplay from "./ViewProfileDisplay"
import { makeAnonymousUser, makeCountries, makeUser } from "../factories/user"
import IntegrationTestHelper from "../util/integration_test_helper"

describe("ViewProfileDisplay", () => {
  let helper, renderPage
  const user = makeUser()
  const countries = makeCountries()

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    helper.handleRequestStub.withArgs("/api/users/me").returns({
      status: 200,
      body:   user
    })
    helper.handleRequestStub.withArgs("/api/countries/").returns({
      status: 200,
      body:   countries
    })
    renderPage = helper.configureReduxQueryRenderer(ViewProfileDisplay)
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders the display for a logged in user", async () => {
    const { wrapper } = await renderPage()
    assert.isTrue(wrapper.find(".profile-btn").exists())
    assert.isTrue(
      wrapper
        .find(".auth-page")
        .text()
        // $FlowFixMe: user.legal_address is not null
        .includes(user.legal_address.street_address[0])
    )
    assert.isTrue(
      wrapper
        .find(".auth-page")
        .text()
        // $FlowFixMe: user.profile is not null
        .includes(user.profile.company)
    )
  })

  it("renders the display for an anonymous user", async () => {
    helper.handleRequestStub.withArgs("/api/users/me").returns({
      status: 200,
      body:   makeAnonymousUser()
    })
    const { wrapper } = await renderPage()
    assert.isFalse(wrapper.find(".submit-row").exists())
    assert.isTrue(
      wrapper
        .find(".auth-page")
        .text()
        .includes("You must be logged in to view your profile.")
    )
  })
})
