// @flow
import { include } from "named-urls";
import UrlAssembler from "url-assembler";
import qs from "query-string";

export const getNextParam = (search: string) => qs.parse(search).next || "/";

export const routes = {
  root: "/",

  // authentication related routes
  profile: include("/profile/", {
    view: "",
    update: "edit/",
  }),

  accountSettings: "/account-settings/",
  logout: "/logout/",

  // authentication related routes
  login: include("/signin/", {
    begin: "",
    password: "password/",
    forgot: include("forgot-password/", {
      begin: "",
      confirm: "confirm/:uid/:token/",
    }),
  }),

  register: include("/create-account/", {
    begin: "",
    confirm: "confirm/",
    confirmSent: "confirm-sent/",
    details: "details/",
    error: "error/",
    extra: "extra/",
    denied: "denied/",
    retry: "retry/",
  }),

  account: include("/account/", {
    confirmEmail: "confirm-email",
  }),

  applications: include("/applications/", {
    dashboard: "",
    paymentHistory: include(":applicationId/payment-history/", {
      self: "",
    }),
  }),

  review: include("/review/", {
    dashboard: "",
    detail: ":submissionId/",
  }),

  resourcePages: include("", {
    howToApply: "apply/",
  }),
};

const api = UrlAssembler().prefix("/api/");

export const submissionsAPI = api.segment("submissions/");
export const submissionDetailAPI = submissionsAPI.segment(":submissionId/");

export const applicationsAPI = api.segment("applications/");
export const applicationDetailAPI = applicationsAPI.segment(":applicationId/");
export const appResumeAPI = applicationDetailAPI.segment("resume/");
export const appVideoInterviewAPI =
  applicationDetailAPI.segment("video-interviews/");

export const paymentAPI = api.segment("v0/payment/");
