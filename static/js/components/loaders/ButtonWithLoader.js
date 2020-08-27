// @flow
import React from "react"
import { Spinner } from "reactstrap"
import Delayed from "./Delayed"

type Props = {
  loading: boolean,
  className?: string,
  children?: any
}
const ButtonWithLoader = (props: Props) => {
  const { loading, children, className, ...otherProps } = props
  return (
    <button
      disabled={loading}
      className={
        className ? `${className} button-with-loader` : "button-with-loader"
      }
      {...otherProps}
    >
      {loading && (
        <Delayed delay={1000}>
          <Spinner type="grow" />
        </Delayed>
      )}
      {children}
    </button>
  )
}

export default ButtonWithLoader
