// @flow
import casual from "casual-browserify";
import { assert } from "chai";

import TakeVideoInterviewDisplay from "./TakeVideoInterviewDisplay";

import IntegrationTestHelper from "../util/integration_test_helper";
import {
  makeApplicationDetail,
  makeApplicationSubmission,
} from "../factories/application";

describe("TakeVideoInterviewDisplay", () => {
  let helper, renderPage, application, stepId, submission;
  beforeEach(() => {
    stepId = casual.integer(0, 100);
    application = makeApplicationDetail();
    submission = {
      ...makeApplicationSubmission(),
      run_application_step_id: stepId,
    };
    application.submissions = [
      makeApplicationSubmission(),
      submission,
      makeApplicationSubmission(),
    ];

    helper = new IntegrationTestHelper();
    renderPage = helper.configureReduxQueryRenderer(TakeVideoInterviewDisplay, {
      application,
      stepId,
    });
  });

  afterEach(() => {
    helper.cleanup();
  });

  it("has a link with the interview URL", async () => {
    const { wrapper } = await renderPage();
    assert.equal(
      wrapper.find(".take-video-interview a.btn-external-link").prop("href"),
      submission.take_interview_url,
    );
  });

  it("shows the interview token", async () => {
    const { wrapper } = await renderPage();
    assert.include(
      wrapper.find(".take-video-interview").text(),
      String(submission.interview_token),
    );
  });
});
