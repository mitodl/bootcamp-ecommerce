// @flow
import React from "react";
import { Spinner } from "reactstrap";

import Delayed from "./Delayed";

type Props = {};
export default class FullLoader extends React.Component<Props> {
  render() {
    return (
      <Delayed delay={1000}>
        <div className="full-loader" aria-hidden={true}>
          <Spinner type="grow" />
          <Spinner type="grow" />
          <Spinner type="grow" />
        </div>
      </Delayed>
    );
  }
}
