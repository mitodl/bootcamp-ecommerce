// @flow
import { assert } from "chai"
import sinon from "sinon"

import EditProfilePage from "./EditProfilePage"
import {
  makeAnonymousUser,
  makeCountries,
  makeUser
} from "../../factories/user"
import IntegrationTestHelper from "../../util/integration_test_helper"

describe("EditProfilePage", () => {
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

    renderPage = helper.configureReduxQueryRenderer(EditProfilePage)
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders the page for a logged in user", async () => {
    const { wrapper } = await renderPage()
    assert.isTrue(wrapper.find("EditProfileForm").exists())
  })

  it("renders the page for an anonymous user", async () => {
    helper.handleRequestStub.withArgs("/api/users/me").returns({
      status: 200,
      body:   makeAnonymousUser()
    })
    const { wrapper } = await renderPage()
    assert.isFalse(wrapper.find("EditProfileForm").exists())
    assert.isTrue(
      wrapper
        .find(".auth-page")
        .text()
        .includes("You must be logged in to edit your profile.")
    )
  })

  //
  ;[true, false].forEach(hasError => {
    it(`submits the updated profile ${
      hasError ? "and received an error" : "successfully"
    }`, async () => {
      const { wrapper } = await renderPage()
      const setSubmitting = helper.sandbox.stub()
      const setErrors = helper.sandbox.stub()
      const values = user
      const actions = {
        setErrors,
        setSubmitting
      }

      helper.handleRequestStub.withArgs("/api/users/me", "PATCH").returns({
        status: 401,
        body:   {
          errors: hasError ? "some errors" : null
        }
      })

      await wrapper.find("EditProfileForm").prop("onSubmit")(values, actions)

      const expectedPayload = {
        ...user,
        profile: {
          ...user.profile
        }
      }
      sinon.assert.calledWith(
        helper.handleRequestStub,
        "/api/users/me",
        "PATCH",
        {
          body:        expectedPayload,
          credentials: undefined,
          headers:     { "X-CSRFTOKEN": null }
        }
      )
      sinon.assert.calledWith(setSubmitting, false)
      assert.equal(setErrors.length, 0)
      if (hasError) {
        assert.isNull(helper.currentLocation)
      } else {
        assert.equal(helper.currentLocation.pathname, "/profile/")
      }
    })
  })
})
