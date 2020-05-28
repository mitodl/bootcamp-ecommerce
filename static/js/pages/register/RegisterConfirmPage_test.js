// @flow
import { assert } from "chai"

import IntegrationTestHelper from "../../util/integration_test_helper"
import RegisterConfirmPage from "./RegisterConfirmPage"
import {
  STATE_REGISTER_BACKEND_EDX,
  STATE_REGISTER_DETAILS
} from "../../lib/auth"

describe("RegisterConfirmPage", () => {
  let helper, renderPage
  const token = "asdf"

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    renderPage = helper.configureReduxQueryRenderer(
      RegisterConfirmPage,
      {
        location: {
          search: ""
        }
      },
      {
        entities: {
          auth: {
            state:         STATE_REGISTER_DETAILS,
            partial_token: token,
            extra_data:    {
              name: "name"
            }
          }
        }
      }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("shows a message when the confirmation page is displayed and redirects", async () => {
    helper.handleRequestStub.returns({})
    const token = "asdf"
    const { wrapper, store } = await renderPage()

    wrapper
      .find("RegisterConfirmPage")
      .instance()
      .componentDidUpdate({})
    assert.deepEqual(store.getState().ui.userNotifications, {
      "email-verified": {
        type:  "text",
        props: {
          text:
            "Success! We've verified your email. Please finish your account creation below."
        }
      }
    })
    assert.equal(helper.currentLocation.pathname, "/create-account/details/")
    assert.equal(
      helper.currentLocation.search,
      `?backend=${STATE_REGISTER_BACKEND_EDX}&partial_token=${token}`
    )
  })
})
