// @flow
import { include } from "named-urls"
import qs from "query-string"

export const getNextParam = (search: string) => qs.parse(search).next || "/"

export const routes = {
  root: "/",

  // authentication related routes
  profile: include("/profile/", {
    view:   "",
    update: "edit/"
  }),

  accountSettings: "/account-settings/",
  logout:          "/logout/",

  // authentication related routes
  login: include("/signin/", {
    begin:    "",
    password: "password/",
    forgot:   include("forgot-password/", {
      begin:   "",
      confirm: "confirm/:uid/:token/"
    })
  }),

  register: include("/create-account/", {
    begin:       "",
    confirm:     "confirm/",
    confirmSent: "confirm-sent/",
    details:     "details/",
    error:       "error/",
    extra:       "extra/",
    denied:      "denied/"
  }),

  account: include("/account/", {
    confirmEmail: "confirm-email"
  }),

  applications: include("/applications/", {
    dashboard: ""
  })
}
