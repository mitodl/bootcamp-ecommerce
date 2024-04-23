// @flow
import React from "react";

import {
  ALERT_TYPE_TEXT,
  CMS_NOTIFICATION_ID_ATTR,
  CMS_NOTIFICATION_LCL_STORAGE_ID,
  CMS_NOTIFICATION_SELECTOR,
  CMS_SITE_WIDE_NOTIFICATION,
} from "../constants";
import { isLocalStorageSupported } from "../util/util";

export const handleCmsNotifications = (addUserNotification: Function) => {
  const cmsNotification = document.querySelector(CMS_NOTIFICATION_SELECTOR);
  if (cmsNotification) {
    const notificationId = cmsNotification.getAttribute(
      CMS_NOTIFICATION_ID_ATTR,
    );
    const notificationHtml = cmsNotification.innerHTML;
    if (
      isLocalStorageSupported() &&
      window.localStorage.getItem(CMS_NOTIFICATION_LCL_STORAGE_ID) !==
        notificationId
    ) {
      addUserNotification({
        [CMS_SITE_WIDE_NOTIFICATION]: {
          type: ALERT_TYPE_TEXT,
          props: {
            text: (
              <div
                className="site-wide"
                dangerouslySetInnerHTML={{ __html: notificationHtml }}
              />
            ),
            persistedId: notificationId,
          },
        },
      });
    }
  }
};
