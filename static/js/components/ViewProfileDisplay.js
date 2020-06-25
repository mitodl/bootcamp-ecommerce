/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query-react"
import { find, fromPairs, propEq } from "ramda"
import { createStructuredSelector } from "reselect"

import { DrawerCloseHeader } from "./Drawer"
import {
  EMPLOYMENT_EXPERIENCE,
  EMPLOYMENT_SIZE,
  GENDER_CHOICES,
  PROFILE_EDIT
} from "../constants"
import queries from "../lib/queries"
import { currentUserSelector } from "../lib/queries/users"
import { setDrawerState } from "../reducers/drawer"

import type { Country, CurrentUser } from "../flow/authTypes"

const TwoColumnRow = (props: {
  label: string,
  children: string | React$Element<*>
}): React$Element<*> => (
  <div className="row profile-row">
    <div className="col-12 col-sm-6 profile-label">{props.label}</div>
    <div className="col-12 col-sm-6">{props.children}</div>
  </div>
)

type StateProps = {|
  currentUser: ?CurrentUser,
  countries: Array<Country>
|}

type DispatchProps = {
  updateDrawer(state): void
}

type Props = {|
  ...StateProps,
  ...DispatchProps
|}

export function ViewProfileDisplay(props: Props) {
  const { currentUser, countries, updateDrawer } = props

  return countries && currentUser ? (
    <div className="container drawer-wrapper view-profile profile-display">
      <DrawerCloseHeader />
      <div className="row">
        <h2 className="col-6">Profile</h2>
        <div className="col-6 text-right">
          <button
            type="submit"
            onClick={() => {
              updateDrawer(PROFILE_EDIT)
            }}
            className="btn-danger"
          >
            Edit
          </button>
        </div>
      </div>
      <div className="row bootcamp-form">
        {currentUser.is_authenticated ? (
          <div className="col-12">
            <TwoColumnRow label="First Name">
              {currentUser.legal_address.first_name}
            </TwoColumnRow>
            <TwoColumnRow label="Last Name">
              {currentUser.legal_address.last_name}
            </TwoColumnRow>
            <TwoColumnRow label="Full Name">
              {currentUser.profile.name}
            </TwoColumnRow>
            {currentUser.legal_address.street_address.map((line, idx) => {
              const addressLineSuffix = idx > 0 ? ` ${idx + 1}` : ""
              return (
                <TwoColumnRow label={`Address${addressLineSuffix}`} key={idx}>
                  {line}
                </TwoColumnRow>
              )
            })}
            {countries && currentUser.legal_address.country ? (
              <TwoColumnRow label="Country">
                {
                  find(
                    propEq("code", currentUser.legal_address.country),
                    countries
                  ).name
                }
              </TwoColumnRow>
            ) : null}
            <TwoColumnRow label="City">
              {currentUser.legal_address.city}
            </TwoColumnRow>
            {countries && currentUser.legal_address.state_or_territory ? (
              <TwoColumnRow label="State/Province/Region">
                {
                  find(
                    propEq(
                      "code",
                      currentUser.legal_address.state_or_territory
                    ),
                    find(
                      propEq("code", currentUser.legal_address.country),
                      countries
                    ).states
                  ).name
                }
              </TwoColumnRow>
            ) : null}
            <div className="divider" />
            <TwoColumnRow label="Gender">
              {fromPairs(GENDER_CHOICES)[currentUser.profile.gender]}
            </TwoColumnRow>
            <TwoColumnRow label="Year of Birth">
              {currentUser.profile.birth_year}
            </TwoColumnRow>
            <TwoColumnRow label="Company">
              {currentUser.profile.company}
            </TwoColumnRow>
            <TwoColumnRow label="Job Title">
              {currentUser.profile.job_title}
            </TwoColumnRow>
            <div className="form-group dotted" />
            <TwoColumnRow label="Industry">
              {currentUser.profile.industry}
            </TwoColumnRow>
            <TwoColumnRow label="Job Function">
              {currentUser.profile.job_function}
            </TwoColumnRow>
            <TwoColumnRow label="Company Size">
              {fromPairs(EMPLOYMENT_SIZE)[currentUser.profile.company_size]}
            </TwoColumnRow>
            <TwoColumnRow label="Years of Work Experience">
              {
                fromPairs(EMPLOYMENT_EXPERIENCE)[
                  currentUser.profile.years_experience
                ]
              }
            </TwoColumnRow>
            <TwoColumnRow label="Highest Level of Education">
              {currentUser.profile.highest_education}
            </TwoColumnRow>
          </div>
        ) : (
          <div className="col-12">
            You must be logged in to view your profile.
          </div>
        )}
      </div>
    </div>
  ) : null
}

const mapStateToProps = createStructuredSelector({
  currentUser: currentUserSelector,
  countries:   queries.users.countriesSelector
})

const mapPropsToConfigs = () => [
  queries.users.currentUserQuery(),
  queries.users.countriesQuery()
]

const mapDispatchToProps = dispatch => ({
  updateDrawer: (newState: ?string) => dispatch(setDrawerState(newState))
})

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(ViewProfileDisplay)
