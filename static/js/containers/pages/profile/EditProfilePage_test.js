// @flow
import { assert } from "chai"
import sinon from "sinon"

import EditProfilePage from "./EditProfilePage"
import {
  makeAnonymousUser,
  makeCountries,
  makeUser
} from "../../../factories/user"
import IntegrationTestHelper from "../../../util/integration_test_helper"
import {queryListResponse} from "../../../lib/test_utils";

describe("EditProfilePage", () => {
  let helper, renderPage
  const user = makeUser()
  const countries = makeCountries()

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    helper.handleRequestStub
      .withArgs("/api/users/me")
      .returns({
        status: 200,
        body: user
      })
    helper.handleRequestStub
      .withArgs("/api/countries/")
      .returns(queryListResponse(countries))

    renderPage = helper.configureReduxQueryRenderer(
      EditProfilePage,
      {
          currentUser: user,
          countries:   countries
      },{
        entities: {
          currentUser: user,
          countries:   countries
        }
      }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders the page for a logged in user", async () => {
    const { wrapper } = await renderPage()
    assert.isTrue(wrapper.find("EditProfileForm").exists())
  })

  it("renders the page for an anonymous user", async () => {
    const { wrapper } = await renderPage({
        currentUser: makeAnonymousUser(),
        countries:   countries
    })
    assert.isFalse(wrapper.find("EditProfileForm").exists())
    assert.isTrue(
      wrapper
        .find(".auth-page")
        .text()
        .includes("You must be logged in to edit your profile.")
    )
  })

  //
  ;[
    [true, true],
    [true, false],
    [false, true],
    [false, false]
  ].forEach(([hasError, hasEmptyFields]) => {
    it(`submits the updated profile ${
      hasEmptyFields ? "with some empty fields " : ""
    }${hasError ? "and received an error" : "successfully"}`, async () => {
      // $FlowFixMe
      user.profile.company_size = hasEmptyFields ? "" : 50
      // $FlowFixMe
      user.profile.years_experience = hasEmptyFields ? "" : 5
      // $FlowFixMe
      user.profile.highest_education = hasEmptyFields ? "" : "Doctorate"

      const { wrapper } = await renderPage()
      const setSubmitting = helper.sandbox.stub()
      const setErrors = helper.sandbox.stub()
      const values = user
      const actions = {
        setErrors,
        setSubmitting
      }

      helper.handleRequestStub.returns({
        body: {
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
      if (hasEmptyFields) {
        // $FlowFixMe
        expectedPayload.profile.company_size = null
        // $FlowFixMe
        expectedPayload.profile.years_experience = null
        // $FlowFixMe
        expectedPayload.profile.highest_education = ""
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
