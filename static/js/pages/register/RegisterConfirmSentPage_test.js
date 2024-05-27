// @flow
/* global SETTINGS: false */
import { assert } from "chai";

import RegisterConfirmSentPage, {
  RegisterConfirmSentPage as InnerRegisterConfirmSentPage,
} from "./RegisterConfirmSentPage";
import IntegrationTestHelper from "../../util/integration_test_helper";

import { routes } from "../../lib/urls";

describe("RegisterConfirmSentPage", () => {
  const userEmail = "test@example.com";
  const supportUrl = "https://test.edu/form";

  let helper, renderPage;

  beforeEach(() => {
    SETTINGS.support_url = supportUrl;

    helper = new IntegrationTestHelper();

    renderPage = helper.configureHOCRenderer(
      RegisterConfirmSentPage,
      InnerRegisterConfirmSentPage,
      {},
      {
        location: {
          search: `?email=${encodeURIComponent(userEmail)}`,
        },
      },
    );
  });

  afterEach(() => {
    helper.cleanup();
  });

  it("displays a link to email support", async () => {
    const { inner } = await renderPage();
    assert.equal(inner.find(".contact-support > a").prop("href"), supportUrl);
  });

  it("displays a link to create account page", async () => {
    const { inner } = await renderPage();
    assert.equal(inner.find("li > a").prop("href"), routes.register.begin);
  });

  it("displays user's email on the page", async () => {
    const { inner } = await renderPage();
    assert.equal(
      inner.find(".auth-card > .col-12 > p > span").text("href"),
      userEmail,
    );
  });
});
