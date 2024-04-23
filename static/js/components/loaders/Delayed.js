// @flow
import React from "react";

type Props = {
  delay?: number,
  children: React$Element<*>,
};
type State = {
  enabled: boolean,
};
export default class Delayed extends React.Component<Props, State> {
  timeoutId: any;

  constructor(props: Props) {
    super(props);
    this.state = {
      enabled: false,
    };
    let delay = props.delay;
    if (delay === undefined) {
      delay = 1000;
    }

    // delay loader temporarily to avoid flickering UI
    this.timeoutId = setTimeout(() => {
      this.setState({ enabled: true });
    }, delay);
  }

  componentWillUnmount() {
    clearTimeout(this.timeoutId);
  }

  render() {
    const { enabled } = this.state;
    return enabled ? this.props.children : null;
  }
}
