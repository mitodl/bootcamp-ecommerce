// @flow
import type {
  Dispatch, Action as ReduxAction
} from 'redux'

export type Dispatcher<T> = (d: Dispatch<*>) => Promise<T>;

export type Action = ReduxAction<string> & {
  payload: any,
};
