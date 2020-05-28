/* global SETTINGS: false */
import { assert } from "chai"

import ApplicationDashboardPage from "./ApplicationDashboardPage"
import IntegrationTestHelper from "../../util/integration_test_helper"
import { APP_STATE_TEXT_MAP } from "../../constants"
import { makeApplication } from "../../factories/application"
import { makeUser } from "../../factories/user"

describe("ApplicationDashboardPage", () => {
  let helper,
    fakeUser,
    renderPage,
    fakeApplications = []

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    fakeApplications = [makeApplication(), makeApplication()]
    fakeUser = makeUser()

    helper.handleRequestStub.withArgs("/api/applications/").returns({
      status: 200,
      body:   fakeApplications
    })

    renderPage = helper.configureReduxQueryRenderer(
      ApplicationDashboardPage,
      {},
      {
        entities: {
          currentUser: fakeUser
        }
      }
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders the user's name", async () => {
    const { wrapper } = await renderPage()
    assert.equal(wrapper.find("h2.name").text(), fakeUser.profile.name)
  })

  it("renders a card for each application that a user has", async () => {
    fakeApplications[0].state = "AWAITING_PROFILE_COMPLETION"
    fakeApplications[1].state = "AWAITING_SUBMISSION_REVIEW"
    const { wrapper } = await renderPage()
    const cards = wrapper.find(".application-card")
    assert.lengthOf(cards, fakeApplications.length)
    for (let i = 0; i < cards.length; i++) {
      assert.equal(
        cards
          .at(i)
          .find("h2")
          .text(),
        fakeApplications[i].bootcamp_run.bootcamp.title
      )
      assert.equal(
        cards
          .at(i)
          .find(".status-col")
          .text(),
        `Application Status: ${APP_STATE_TEXT_MAP[fakeApplications[i].state]}`
      )
    }
  })

  it("renders a thumbnail for an applied bootcamp if one exists", async () => {
    fakeApplications[0].bootcamp_run.page.thumbnail_image_src = null
    fakeApplications[1].bootcamp_run.page.thumbnail_image_src =
      "http://example.com/img.jpg"
    const { wrapper } = await renderPage()
    const cards = wrapper.find(".application-card")
    assert.isFalse(
      cards
        .at(0)
        .find("img")
        .exists()
    )
    assert.isTrue(
      cards
        .at(1)
        .find("img")
        .exists()
    )
  })
})