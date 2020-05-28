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
    console.log(payload)
    try {
      const {
        body: { errors }
      }: // $FlowFixMe
      { body: Object } = await editProfile(payload)

      if (errors && errors.length > 0) {
        console.log(errors)
        setErrors({
          email: errors[0]
        })
      } else {
        history.push(routes.profile.view)
      }
    } finally {
      setSubmitting(false)
      console.log("done")
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
