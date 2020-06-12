// @flow
/* global SETTINGS: false */
import React from "react"

type DetailRowProps = {
  className: string,
  fulfilled: boolean,
  children?: React$Node
}

/*
 * Renders a section of the application progress bar (with a checkbox if this step is complete) along with the
 * detail content of the application step.
 */
export default function ProgressDetailRow(
  props: DetailRowProps
): React$Element<*> {
  const { children, className, fulfilled } = props

  return (
    <div
      className={`detail-section ${className}${fulfilled ? " fulfilled" : ""}`}
    >
      <div className="d-flex">
        <div className="progress-meter">
          <div className="top-line" />
          <div className="check">
            {fulfilled && <i className="material-icons">done</i>}
          </div>
          <div className="bottom-line" />
        </div>
        <div className="container no-gutters p-0 mb-2 detail-content">
          <div className="row no-gutters w-100 justify-content-between">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}
