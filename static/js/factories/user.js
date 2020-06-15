// @flow
import casual from "casual-browserify"
import moment from "moment"

import { incrementer } from "../util/util"

import type { AnonymousUser, LoggedInUser } from "../flow/authTypes"

const incr = incrementer()

export const makeAnonymousUser = (): AnonymousUser => ({
  is_anonymous:     true,
  is_authenticated: false
})

export const makeUser = (username: ?string): LoggedInUser => ({
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  id:               incr.next().value,
  // $FlowFixMe: Flow thinks incr.next().value may be undefined, but it won't ever be
  username:         username || `${casual.word}_${incr.next().value}`,
  email:            casual.email,
  name:             casual.full_name,
  is_anonymous:     false,
  is_authenticated: true,
  created_on:       casual.moment.format(),
  updated_on:       casual.moment.format(),
  profile:          {
    name:              casual.full_name,
    gender:            "f",
    birth_year:        1980,
    company:           casual.company_name,
    company_size:      99,
    industry:          "Education",
    job_title:         casual.word,
    job_function:      "Administrative",
    years_experience:  20,
    highest_education: "Doctorate",
    is_complete:       true,
    updated_on:        casual.moment.format()
  },
  legal_address: {
    street_address:     [casual.street],
    first_name:         casual.first_name,
    last_name:          casual.last_name,
    city:               casual.city,
    state_or_territory: "US-MA",
    country:            "US",
    postal_code:        "02090"
  },
  unused_coupons: []
})

export const makeCompleteUser = (username: ?string): LoggedInUser => {
  const fakeUser = makeUser(username)
  // $FlowFixMe: Profile can't be undefined
  fakeUser.profile.name = moment().format()
  // $FlowFixMe: Profile can't be undefined
  fakeUser.profile.updated_on = moment().format()
  // $FlowFixMe: Profile can't be undefined
  fakeUser.profile.is_complete = true
  return fakeUser
}

export const makeIncompleteUser = (username: ?string): LoggedInUser => {
  const fakeUser = makeUser(username)
  // $FlowFixMe: Profile can't be undefined
  fakeUser.profile.name = undefined
  // $FlowFixMe: Profile can't be undefined
  fakeUser.profile.is_complete = false
  return fakeUser
}

export const makeCountries = () => [
  {
    code:   "US",
    name:   "United States",
    states: [
      { code: "US-CO", name: "Colorado" },
      { code: "US-MA", name: "Massachusetts" }
    ]
  },
  {
    code:   "CA",
    name:   "Canada",
    states: [
      { code: "CA-QC", name: "Quebec" },
      { code: "CA-NS", name: "Nova Scotia" }
    ]
  },
  { code: "FR", name: "France", states: [] },
  { code: "GB", name: "United Kingdom", states: [] }
]
