// @flow
import { useCallback } from "react";
import * as React from "react";
import { useDispatch, useSelector } from "react-redux";
import { Drawer as RMWCDrawer, DrawerContent } from "@rmwc/drawer";
import { Theme } from "@rmwc/theme";
import * as R from "ramda";

import { drawerSelector } from "../lib/selectors";
import { closeDrawer } from "../reducers/drawer";
import {
  NEW_APPLICATION,
  PAYMENT,
  PROFILE_EDIT,
  PROFILE_VIEW,
  TAKE_VIDEO_INTERVIEW,
  RESUME_UPLOAD,
} from "../constants";

import EditProfileDisplay from "./EditProfileDisplay";
import ViewProfileDisplay from "./ViewProfileDisplay";
import PaymentDisplay from "./PaymentDisplay";
import NewApplication from "./NewApplication";
import TakeVideoInterviewDisplay from "./TakeVideoInterviewDisplay";
import ResumeLinkedIn from "./ResumeLinkedIn";

export const DrawerCloseHeader = (): React$Element<*> => {
  const dispatch = useDispatch();
  const onClick = useCallback(() => {
    dispatch(closeDrawer(false));
  }, [dispatch]);

  return (
    <div className="drawer-close">
      <button onClick={onClick} className="btn-plain d-flex">
        <i className="material-icons">close</i>
      </button>
    </div>
  );
};

const renderDrawerContents = (
  drawerState: string,
  drawerMeta: ?Object,
): ?React$Element<*> => {
  switch (drawerState) {
    case PROFILE_EDIT:
      return <EditProfileDisplay />;
    case PROFILE_VIEW:
      return <ViewProfileDisplay />;
    case PAYMENT:
      return <PaymentDisplay application={R.prop("application", drawerMeta)} />;
    case NEW_APPLICATION:
      return (
        <NewApplication appliedRunIds={R.prop("appliedRunIds", drawerMeta)} />
      );
    case RESUME_UPLOAD:
      return (
        <ResumeLinkedIn applicationId={R.prop("applicationId", drawerMeta)} />
      );
    case TAKE_VIDEO_INTERVIEW:
      return (
        <TakeVideoInterviewDisplay
          application={R.prop("application", drawerMeta)}
          stepId={R.prop("stepId", drawerMeta)}
        />
      );
    default:
      return null;
  }
};

export default function Drawer() {
  const { drawerOpen, drawerState, drawerMeta } = useSelector(drawerSelector);

  const dispatch = useDispatch();
  const onClose = useCallback(() => {
    dispatch(closeDrawer());
  }, [dispatch]);

  return (
    <Theme>
      <RMWCDrawer open={drawerOpen} onClose={onClose} dir="rtl" modal>
        <DrawerContent dir="ltr">
          <DrawerCloseHeader />
          {renderDrawerContents(drawerState, drawerMeta)}
        </DrawerContent>
      </RMWCDrawer>
    </Theme>
  );
}
