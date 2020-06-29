// @flow
import React from "react"

// this component is inteded to take care of accessibility concerns
// when using an anchor tag as a click target without an href

type Props = {
  onClick: Function,
  className: string,
  children: React$Node
}

export default function AccessibleAnchor(props: Props) {
  const { onClick, className, children } = props

  return (
    <a
      className={className}
      tabIndex="0"
      onClick={onClick}
      onKeyPress={e => {
        if (e.key === "Enter") {
          onClick()
        }
      }}
    >
      {children}
    </a>
  )
}
