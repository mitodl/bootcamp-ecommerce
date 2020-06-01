// @flow
/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query-react"
import { mutateAsync } from "redux-query"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import { EDIT_PROFILE_PAGE_TITLE, PROFILE_VIEW } from "../constants"
import users, { currentUserSelector } from "../lib/queries/users"
import queries from "../lib/queries"
import { formatTitle } from "../util/util"

import EditProfileForm from "./forms/EditProfileForm"

import type {
  Country,
  CurrentUser,
  User,
  HttpAuthResponse
} from "../flow/authTypes"
import { setDrawerState } from "../reducers/drawer"

type StateProps = {|
  countries: ?Array<Country>,
  currentUser: CurrentUser
|}

type DispatchProps = {|
  editProfile: (userProfileData: User) => Promise<HttpAuthResponse<User>>,
  updateDrawer: (state: Object) => void
|}

type Props = {|
  ...StateProps,
  ...DispatchProps
|}

export class EditProfileDisplay extends React.Component<Props> {
  async onSubmit(profileData: User, { setSubmitting, setErrors }: Object) {
    const { editProfile, updateDrawer } = this.props
    const payload = {
      ...profileData,
      ...(profileData.profile ?
        {
          profile: {
            ...profileData.profile
          }
        } :
        {})
    }
    try {
      const {
        body: { errors }
      }: // $FlowFixMe
      { body: Object } = await editProfile(payload)

      if (errors && errors.length > 0) {
        setErrors({
          email: errors[0]
        })
      } else {
        updateDrawer(PROFILE_VIEW)
      }
    } finally {
      setSubmitting(false)
    }
  }

  render() {
    const { countries, currentUser } = this.props
    return countries && currentUser ? (
      <div className="container auth-page registration-page">
        <MetaTags>
          <title>{formatTitle(EDIT_PROFILE_PAGE_TITLE)}</title>
        </MetaTags>
        <EditProfileForm
          countries={countries}
          user={currentUser}
          onSubmit={this.onSubmit.bind(this)}
        />
      </div>
    ) : null
  }
}

const editProfile = (userProfileData: User) =>
  mutateAsync(users.editProfileMutation(userProfileData))

const mapStateToProps = createStructuredSelector({
  currentUser: currentUserSelector,
  countries:   queries.users.countriesSelector
})

const mapDispatchToProps = dispatch => ({
  editProfile:  (data: User) => dispatch(editProfile(data)),
  updateDrawer: (newState: ?string) => dispatch(setDrawerState(newState))
})

const mapPropsToConfigs = () => [
  queries.users.countriesQuery(),
  queries.users.currentUserQuery()
]

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(EditProfileDisplay)
