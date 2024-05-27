// @flow
/* global SETTINGS: false */
import React from "react";
import { compose } from "redux";
import { connect } from "react-redux";
import { connectRequest } from "redux-query-react";
import { mutateAsync } from "redux-query";
import { createStructuredSelector } from "reselect";

import EditProfileForm from "./forms/EditProfileForm";

import { PROFILE_VIEW } from "../constants";
import users, { currentUserSelector } from "../lib/queries/users";
import queries from "../lib/queries";
import { getFirstResponseBodyError, isErrorResponse } from "../util/util";
import { setDrawerState } from "../reducers/drawer";

import type {
  Country,
  CurrentUser,
  User,
  HttpAuthResponse,
  EditProfileResponse,
} from "../flow/authTypes";
import SupportLink from "./SupportLink";

type StateProps = {|
  countries: ?Array<Country>,
  currentUser: CurrentUser,
|};

type DispatchProps = {|
  editProfile: (userProfileData: User) => Promise<HttpAuthResponse<User>>,
  updateDrawer: (state: Object) => void,
|};

type Props = {|
  ...StateProps,
  ...DispatchProps,
|};

export class EditProfileDisplay extends React.Component<Props> {
  async onSubmit(profileData: User, { setSubmitting, setErrors }: Object) {
    const { editProfile, updateDrawer } = this.props;
    const payload = {
      ...profileData,
      ...(profileData.profile
        ? {
            profile: {
              ...profileData.profile,
            },
          }
        : {}),
    };
    try {
      const response: EditProfileResponse = await editProfile(payload);
      if (isErrorResponse(response)) {
        const responseBodyError = getFirstResponseBodyError(response);
        setErrors({
          general: responseBodyError || (
            <span>
              Something went wrong while updating your profile. Please refresh
              the page and try again, or <SupportLink />
            </span>
          ),
        });
      } else {
        updateDrawer(PROFILE_VIEW);
      }
    } finally {
      setSubmitting(false);
    }
  }

  render() {
    const { countries, currentUser } = this.props;
    return countries && currentUser ? (
      <div className="container drawer-wrapper edit-profile profile-display">
        <EditProfileForm
          countries={countries}
          user={currentUser}
          onSubmit={this.onSubmit.bind(this)}
        />
      </div>
    ) : null;
  }
}

const editProfile = (userProfileData: User) =>
  mutateAsync(users.editProfileMutation(userProfileData));

const mapStateToProps = createStructuredSelector({
  currentUser: currentUserSelector,
  countries: queries.users.countriesSelector,
});

const mapDispatchToProps = (dispatch) => ({
  editProfile: (data: User) => dispatch(editProfile(data)),
  updateDrawer: (newState: ?string) => dispatch(setDrawerState(newState)),
});

const mapPropsToConfigs = () => [
  queries.users.countriesQuery(),
  queries.users.currentUserQuery(),
];

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfigs),
)(EditProfileDisplay);
