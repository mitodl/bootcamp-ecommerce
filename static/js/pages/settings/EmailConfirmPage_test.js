// @flow
import { assert } from "chai";

import IntegrationTestHelper from "../../util/integration_test_helper";
import EmailConfirmPage from "./EmailConfirmPage";

describe("EmailConfirmPage", () => {
  let helper, renderPage;

  beforeEach(() => {
    helper = new IntegrationTestHelper();
    renderPage = helper.configureReduxQueryRenderer(EmailConfirmPage, {
      location: {
        search: "",
      },
    });
  });

  afterEach(() => {
    helper.cleanup();
  });

  it("shows a message when the confirmation page is displayed", async () => {
    helper.handleRequestStub.returns({
      status: 200,
      body: {
        confirmed: true,
      },
    });
    const { wrapper, store } = await renderPage();

    wrapper.find("EmailConfirmPage").instance().componentDidUpdate({});
    assert.deepEqual(store.getState().ui.userNotifications, {
      "email-verified": {
        type: "text",
        props: {
          text: "Success! We've verified your email. You email has been updated.",
        },
      },
    });
  });

  it("shows a message when the error page is displayed", async () => {
    helper.handleRequestStub.returns({
      status: 200,
      body: {
        confirmed: false,
      },
    });
    const { wrapper, store } = await renderPage();

    wrapper.find("EmailConfirmPage").instance().componentDidUpdate({});
    assert.deepEqual(store.getState().ui.userNotifications, {
      "email-verified": {
        type: "text",
        color: "danger",
        props: {
          text: "Error! No confirmation code was provided or it has expired.",
        },
      },
    });
  });
});
