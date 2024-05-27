// @flow
import React from "react";
import { compose } from "redux";
import { connect } from "react-redux";

import SiteNavbar from "../components/SiteNavbar";
import NotificationContainer from "../components/notifications/NotificationContainer";
import { addUserNotification } from "../actions";
import { handleCmsNotifications } from "../lib/notifications";

export class HeaderApp extends React.Component<*, *> {
  componentDidMount() {
    const { addUserNotification } = this.props;
    handleCmsNotifications(addUserNotification);
  }

  render() {
    return (
      <React.Fragment>
        <SiteNavbar />
        <NotificationContainer />
      </React.Fragment>
    );
  }
}

const mapDispatchToProps = {
  addUserNotification,
};

export default compose(connect(null, mapDispatchToProps))(HeaderApp);
