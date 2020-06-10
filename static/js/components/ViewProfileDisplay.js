/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query-react"
import { find, fromPairs, propEq } from "ramda"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import {
  EMPLOYMENT_EXPERIENCE,
  EMPLOYMENT_SIZE,
  GENDER_CHOICES,
  PROFILE_EDIT,
  VIEW_PROFILE_PAGE_TITLE
} from "../constants"
import queries from "../lib/queries"
import { currentUserSelector } from "../lib/queries/users"
import { formatTitle } from "../util/util"

import type { Country, CurrentUser } from "../flow/authTypes"
import { setDrawerState } from "../reducers/drawer"

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
    <div className="container auth-page registration-page">
      <MetaTags>
        <title>{formatTitle(VIEW_PROFILE_PAGE_TITLE)}</title>
      </MetaTags>
      <div className="auth-header row">
        <h1 className="col-6">Profile</h1>
        <div className="col-6 profile-button-col">
          <button
            type="submit"
            onClick={() => {
              updateDrawer(PROFILE_EDIT)
            }}
            className="btn btn-danger profile-btn"
          >
            Edit
          </button>
        </div>
      </div>
      <div className="auth-card card-shadow row">
        <div className="container profile-container ">
          <div className="row">
            {currentUser.is_authenticated ? (
              <div className="col-12 auth-form">
                <div className="row profile-row">
                  <div className="col profile-label">First Name</div>
                  <div className="col">
                    {currentUser.legal_address.first_name}
                  </div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">Last Name</div>
                  <div className="col">
                    {currentUser.legal_address.last_name}
                  </div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">Full Name</div>
                  <div className="col">{currentUser.profile.name}</div>
                </div>
                {currentUser.legal_address.street_address.map((line, idx) => (
                  <div className="row profile-row" key={idx}>
                    <div className="col profile-label">
                      Address{idx > 0 ? ` ${idx + 1}` : ""}
                    </div>
                    <div className="col">{line}</div>
                  </div>
                ))}
                {countries && currentUser.legal_address.country ? (
                  <div className="row profile-row">
                    <div className="col profile-label">Country</div>
                    <div className="col">
                      {
                        find(
                          propEq("code", currentUser.legal_address.country),
                          countries
                        ).name
                      }
                    </div>
                  </div>
                ) : null}
                <div className="row profile-row">
                  <div className="col profile-label">City</div>
                  <div className="col">{currentUser.legal_address.city}</div>
                </div>
                {countries && currentUser.legal_address.state_or_territory ? (
                  <div className="row profile-row">
                    <div className="col profile-label">
                      State/Province/Region
                    </div>
                    <div className="col">
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
                    </div>
                  </div>
                ) : null}
                <div className="divider" />
                <div className="row profile-row">
                  <div className="col profile-label">Gender</div>
                  <div className="col">
                    {fromPairs(GENDER_CHOICES)[currentUser.profile.gender]}
                  </div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">Year of Birth</div>
                  <div className="col">{currentUser.profile.birth_year}</div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">Company</div>
                  <div className="col">{currentUser.profile.company}</div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">Job Title</div>
                  <div className="col">{currentUser.profile.job_title}</div>
                </div>
                <div className="form-group dotted" />
                <div className="row profile-row">
                  <div className="col profile-label">Industry</div>
                  <div className="col">{currentUser.profile.industry}</div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">Job Function</div>
                  <div className="col">{currentUser.profile.job_function}</div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">Company Size</div>
                  <div className="col">
                    {
                      fromPairs(EMPLOYMENT_SIZE)[
                        currentUser.profile.company_size
                      ]
                    }
                  </div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">
                    Years of Work Experience
                  </div>
                  <div className="col">
                    {
                      fromPairs(EMPLOYMENT_EXPERIENCE)[
                        currentUser.profile.years_experience
                      ]
                    }
                  </div>
                </div>
                <div className="row profile-row">
                  <div className="col profile-label">
                    Highest Level of Education
                  </div>
                  <div className="col">
                    {currentUser.profile.highest_education}
                  </div>
                </div>
              </div>
            ) : (
              <div className="col-12 auth-form">
                <div className="row">
                  You must be logged in to view your profile.
                </div>
              </div>
            )}
          </div>
        </div>
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
