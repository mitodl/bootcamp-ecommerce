// @flow
import { objOf, pathOr } from "ramda"
import { nextState } from "./util"

import type {
  CurrentUser,
  Country,
  UserProfileForm
} from "../../flow/authTypes"
import { getCookie } from "../api"

export const currentUserSelector = (state: any): ?CurrentUser =>
  state.entities.currentUser

// project the result into entities.currentUser
const transformCurrentUser = objOf("currentUser")

const updateResult = {
  currentUser: nextState
}

const DEFAULT_OPTIONS = {
  options: {
    method:  "PATCH",
    headers: {
      "X-CSRFTOKEN": getCookie("csrftoken")
    }
  }
}

export default {
  currentUserQuery: () => ({
    url:       "/api/users/me",
    transform: transformCurrentUser,
    update:    updateResult
  }),
  countriesSelector: pathOr(null, ["entities", "countries"]),
  countriesQuery:    () => ({
    queryKey:  "countries",
    url:       "/api/countries/",
    transform: objOf("countries"),
    update:    {
      countries: (prev: Array<Country>, next: Array<Country>) => next
    }
  }),
  editProfileMutation: (profileData: UserProfileForm) => ({
    ...DEFAULT_OPTIONS,
    url:  "/api/users/me",
    body: {
      ...profileData
    },
    transform: transformCurrentUser,
    update:    updateResult
  })
}
