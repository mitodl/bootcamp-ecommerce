// @flow
/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query-react"
import { mutateAsync } from "redux-query"
import { createStructuredSelector } from "reselect"
import { MetaTags } from "react-meta-tags"

import { EDIT_PROFILE_PAGE_TITLE } from "../../constants"
import users, { currentUserSelector } from "../../lib/queries/users"
import { routes } from "../../lib/urls"
import queries from "../../lib/queries"
import { formatTitle } from "../../util/util"

import EditProfileForm from "../../components/forms/EditProfileForm"

import type { RouterHistory } from "react-router"
import type {
  Country,
  CurrentUser,
  User,
  HttpAuthResponse
} from "../../flow/authTypes"

type StateProps = {|
  countries: ?Array<Country>,
  currentUser: CurrentUser
|}

type DispatchProps = {|
  editProfile: (userProfileData: User) => Promise<HttpAuthResponse<User>>
|}

type ProfileProps = {|
  history: RouterHistory
|}

type Props = {|
  ...StateProps,
  ...DispatchProps,
  ...ProfileProps
|}

export class EditProfilePage extends React.Component<Props> {
  async onSubmit(profileData: User, { setSubmitting, setErrors }: Object) {
    const { editProfile, history } = this.props

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
        history.push(routes.profile.view)
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
        <div className="auth-header row">
          <h1 className="col-6">Profile</h1>
          <div className="col-6 profile-button-col">
            <button
              type="submit"
              onClick={() => {
                history.push(routes.profile.update)
              }}
              className="btn btn-danger profile-btn"
            >
              Save
            </button>
          </div>
        </div>
        <div className="auth-card card-shadow row">
          <div className="container">
            <div className="row">
              <div className="col-12 auth-form">
                {currentUser.is_authenticated ? (
                  <EditProfileForm
                    countries={countries}
                    user={currentUser}
                    onSubmit={this.onSubmit.bind(this)}
                  />
                ) : (
                  <div className="row">
                    You must be logged in to edit your profile.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
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

const mapDispatchToProps = {
  editProfile: editProfile
}

const mapPropsToConfigs = () => [
  queries.users.countriesQuery(),
  queries.users.currentUserQuery()
]

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs)
)(EditProfilePage)
