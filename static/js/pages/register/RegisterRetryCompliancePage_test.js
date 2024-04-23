// @flow
import { assert } from "chai";
import sinon from "sinon";

import RegisterRetryCompliancePage from "./RegisterRetryCompliancePage";
import IntegrationTestHelper from "../../util/integration_test_helper";
import {
  STATE_REGISTER_EXTRA_DETAILS,
  STATE_USER_BLOCKED,
  STATE_ERROR,
  STATE_ERROR_TEMPORARY,
  FLOW_REGISTER,
  STATE_REGISTER_BACKEND_EDX,
  STATE_REGISTER_BACKEND_EMAIL,
} from "../../lib/auth";
import { routes } from "../../lib/urls";
import { makeRegisterAuthResponse } from "../../factories/auth";
import { makeCountries, makeUser } from "../../factories/user";

describe("RegisterRetryCompliancePage", () => {
  const countries = makeCountries();
  const retryData = {
    profile: {
      name: "Joe",
    },
    legal_address: {
      address: "Elm St",
    },
  };
  const partialToken = "partialTokenTestValue";
  const body = {
    flow: FLOW_REGISTER,
    partial_token: partialToken,
    ...retryData,
  };
  let helper, renderPage, setSubmittingStub, setErrorsStub, user;

  beforeEach(() => {
    user = makeUser();
    helper = new IntegrationTestHelper();
    helper.handleRequestStub.withArgs("/api/countries/").returns({
      status: 200,
      body: countries,
    });

    helper.handleRequestStub.withArgs("/api/register/email/retry").returns({
      body: makeRegisterAuthResponse({
        state: STATE_ERROR_TEMPORARY,
        extra_data: user,
      }),
    });

    setSubmittingStub = helper.sandbox.stub();
    setErrorsStub = helper.sandbox.stub();

    renderPage = helper.configureReduxQueryRenderer(
      RegisterRetryCompliancePage,
      {
        location: {
          search: `?backend=${STATE_REGISTER_BACKEND_EDX}&partial_token=${partialToken}&errors=CS_150`,
        },
      },
    );
  });

  afterEach(() => {
    helper.cleanup();
  });

  it("displays a form", async () => {
    const { wrapper } = await renderPage();
    wrapper.find("RegisterRetryCompliancePage").setState({ user: user });
    wrapper.update();
    const detailsForm = wrapper.find("RegisterDetailsForm");
    assert.isFalse(detailsForm.prop("includePassword"));
  });

  it("handles onSubmit for an error response", async () => {
    const { wrapper } = await renderPage();
    wrapper.find("RegisterRetryCompliancePage").setState({ user: user });
    wrapper.update();
    const error = "error message";
    const fieldErrors = {
      name: error,
    };

    helper.handleRequestStub.returns({
      body: makeRegisterAuthResponse({
        state: STATE_ERROR,
        field_errors: fieldErrors,
      }),
    });

    const onSubmit = wrapper.find("RegisterDetailsForm").prop("onSubmit");

    await onSubmit(retryData, {
      setSubmitting: setSubmittingStub,
      setErrors: setErrorsStub,
    });

    sinon.assert.calledWith(
      helper.handleRequestStub,
      `/api/register/${STATE_REGISTER_BACKEND_EDX}/retry/`,
      "POST",
      { body, headers: undefined, credentials: undefined },
    );

    assert.lengthOf(helper.browserHistory, 1);
    sinon.assert.calledWith(setErrorsStub, fieldErrors);
    sinon.assert.calledWith(setSubmittingStub, false);
  });

  //
  [
    [
      STATE_ERROR_TEMPORARY,
      ["Error code: CS_0"],
      routes.register.retry,
      STATE_REGISTER_BACKEND_EDX,
      `?backend=${STATE_REGISTER_BACKEND_EDX}&errors=Error%20code%3A%20CS_0&partial_token=new_partial_token`,
      1,
    ],
    [
      STATE_ERROR_TEMPORARY,
      ["Error code: CS_150"],
      routes.register.retry,
      STATE_REGISTER_BACKEND_EMAIL,
      `?backend=${STATE_REGISTER_BACKEND_EMAIL}&errors=Error%20code%3A%20CS_150&partial_token=new_partial_token`,
      1,
    ],
    [
      STATE_ERROR,
      [],
      routes.register.error,
      STATE_REGISTER_BACKEND_EMAIL,
      "",
      2,
    ], // cover the case with an error but no  messages
    [
      STATE_REGISTER_EXTRA_DETAILS,
      [],
      routes.register.extra,
      STATE_REGISTER_BACKEND_EDX,
      `?backend=${STATE_REGISTER_BACKEND_EDX}&partial_token=new_partial_token`,
      2,
    ],
    [
      STATE_REGISTER_EXTRA_DETAILS,
      [],
      routes.register.extra,
      STATE_REGISTER_BACKEND_EMAIL,
      `?backend=${STATE_REGISTER_BACKEND_EMAIL}&partial_token=new_partial_token`,
      2,
    ],
    [
      STATE_USER_BLOCKED,
      ["Error code: CS_700"],
      routes.register.denied,
      STATE_REGISTER_BACKEND_EMAIL,
      "?error=Error%20code%3A%20CS_700",
      2,
    ],
    [
      STATE_USER_BLOCKED,
      ["Error code: CS_700"],
      routes.register.denied,
      STATE_REGISTER_BACKEND_EDX,
      "?error=Error%20code%3A%20CS_700",
      2,
    ],
  ].forEach(([state, errors, pathname, backend, search, count]) => {
    it(`redirects to ${pathname} when it receives auth state ${state} for backend ${backend}`, async () => {
      const { wrapper } = await helper.configureReduxQueryRenderer(
        RegisterRetryCompliancePage,
        {
          location: {
            search: `?backend=${backend}&partial_token=${partialToken}`,
          },
        },
      )();
      wrapper.find("RegisterRetryCompliancePage").setState({ user: user });
      wrapper.update();
      helper.handleRequestStub.returns({
        body: makeRegisterAuthResponse({
          state,
          errors,
          backend,
          partial_token: "new_partial_token",
        }),
      });

      const onSubmit = wrapper.find("RegisterDetailsForm").prop("onSubmit");

      await onSubmit(retryData, {
        setSubmitting: setSubmittingStub,
        setErrors: setErrorsStub,
      });

      sinon.assert.calledWith(
        helper.handleRequestStub,
        `/api/register/${backend}/retry/`,
        "POST",
        { body, headers: undefined, credentials: undefined },
      );

      assert.lengthOf(helper.browserHistory, count);
      if (state !== STATE_ERROR_TEMPORARY) {
        assert.include(helper.browserHistory.location, {
          pathname,
          search,
        });
      } else {
        assert.include(window.location.pathname, pathname);
        assert.include(window.location.search, search);
      }

      if (state === STATE_ERROR) {
        sinon.assert.calledWith(setErrorsStub, {});
      } else {
        sinon.assert.notCalled(setErrorsStub);
      }
      sinon.assert.calledWith(setSubmittingStub, false);
    });
  });
});
