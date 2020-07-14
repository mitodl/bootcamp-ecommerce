// @flow
/* global SETTINGS: false */
import React from "react"

type Props = {
  className?: string
}

const SupportLink = (props: Props): React$Element<*> => (
  <React.Fragment>
    <a
      href={SETTINGS.support_url}
      target="_blank"
      rel="noopener noreferrer"
      {...(props.className ? { className: props.className } : {})}
    >
      contact support
    </a>{" "}
    to resolve this issue.
  </React.Fragment>
)

export default SupportLink
