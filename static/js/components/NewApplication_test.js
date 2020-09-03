/* global SETTINGS: false */
import React from "react"
import { assert } from "chai"
import sinon from "sinon"
import wait from "waait"
import { last, prop } from "ramda"
import { shallow } from "enzyme"

import NewApplication, {
  NewApplication as InnerNewApplication
} from "./NewApplication"
import IntegrationTestHelper from "../util/integration_test_helper"
import { makeUser } from "../factories/user"
import { generateFakeRun } from "../factories"
import { isIf, shouldIf } from "../lib/test_utils"

describe("NewApplication", () => {
  const getBootcampsUrl = "/api/bootcampruns/?available=true"
  let helper, fakeUser, fakeBootcampRuns, fakeAppliedId, renderPage

  beforeEach(() => {
    helper = new IntegrationTestHelper()
    fakeUser = makeUser()
    fakeBootcampRuns = [generateFakeRun(), generateFakeRun(), generateFakeRun()]
    // Get the id of the last created run and include it in the list of ids that are already applied
    fakeAppliedId = prop("id", last(fakeBootcampRuns))

    helper.handleRequestStub.withArgs(getBootcampsUrl).returns({
      status: 200,
      body:   fakeBootcampRuns
    })

    renderPage = helper.configureReduxQueryRenderer(
      NewApplication,
      { appliedRunIds: [fakeAppliedId] },
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

  it("shows a dropdown with all available bootcamp runs that aren't already applied to", async () => {
    const { wrapper } = await renderPage()
    const dropdownItems = wrapper.find("DropdownItem")
    assert.lengthOf(dropdownItems, fakeBootcampRuns.length - 1)
    for (let i = 0; i < dropdownItems.length; i++) {
      const dropdownItem = dropdownItems.at(i)
      const bootcampRun = fakeBootcampRuns[i]
      assert.equal(dropdownItem.prop("value"), bootcampRun.run_key)
      assert.equal(dropdownItem.text(), bootcampRun.display_title)
    }
    assert.equal(wrapper.find("DropdownToggle").text(), "Select...")
    // Submit/continue button should be disabled before selecting a bootcamp
    assert.isTrue(
      wrapper
        .find("button")
        .last()
        .prop("disabled")
    )
  })

  it("shows a message if no bootcamps are available for application", async () => {
    helper.handleRequestStub.withArgs(getBootcampsUrl).returns({
      status: 200,
      body:   []
    })

    const { wrapper } = await renderPage()
    assert.isFalse(wrapper.find("Dropdown").exists())
    const message = wrapper.find("p")
    assert.equal(
      message.text(),
      "There are no bootcamps that are currently open for application."
    )
  })

  it("allows a user to select a bootcamp and submit the form to create a new application", async () => {
    const fakeNewApplication = generateFakeRun()
    const newApplicationStub = helper.handleRequestStub
      .withArgs("/api/applications/", "POST")
      .returns({
        status: 201,
        body:   fakeNewApplication
      })

    const { wrapper, store } = await renderPage()
    await wrapper.find("Dropdown").simulate("click")
    await wait()
    wrapper.update()

    const firstBootcampItem = wrapper.find("DropdownItem").at(0)
    await firstBootcampItem.simulate("click")
    await wait()
    wrapper.update()

    assert.equal(
      wrapper.find("DropdownToggle").text(),
      fakeBootcampRuns[0].display_title
    )
    const submitBtn = wrapper.find("button").last()
    assert.isNotOk(submitBtn.prop("disabled"))
    await submitBtn.simulate("click")
    await wait()
    wrapper.update()

    sinon.assert.calledOnce(newApplicationStub)
    assert.deepEqual(store.getState().entities.applications, [
      fakeNewApplication
    ])
  })

  //
  ;[
    [true, true, true, true],
    [true, false, false, false],
    [false, true, true, true],
    [false, false, true, false]
  ].forEach(
    ([hasSelectedBootcamp, pending, expectedDisabled, expectedSpinner]) => {
      it(`if a bootcamp ${isIf(
        hasSelectedBootcamp
      )} selected and API request ${isIf(
        pending
      )} pending, then the button ${shouldIf(
        expectedDisabled
      )} be disabled, and a spinner ${shouldIf(
        expectedSpinner
      )} be shown`, async () => {
        helper.isLoadingStub.returns(pending)
        const wrapper = shallow(
          <InnerNewApplication
            currentUser={fakeUser}
            bootcampRuns={fakeBootcampRuns}
            appliedRunIds={[fakeAppliedId]}
            createAppIsPending={pending}
          />
        )
        if (hasSelectedBootcamp) {
          wrapper.setState({
            selectedBootcamp: fakeBootcampRuns[0]
          })
        }

        assert.equal(
          wrapper.find("ButtonWithLoader").prop("disabled"),
          expectedDisabled
        )
        assert.equal(
          wrapper.find("ButtonWithLoader").prop("loading"),
          expectedSpinner
        )
      })
    }
  )
})
