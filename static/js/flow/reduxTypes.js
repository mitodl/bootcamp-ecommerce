// @flow
import type {
  Dispatch,
} from 'redux';

export type Dispatcher<T> = (d: Dispatch) => Promise<T>;

export type ActionType = string;

export type Action = {
  type: ActionType,
  payload: any,
  meta: null,
};
