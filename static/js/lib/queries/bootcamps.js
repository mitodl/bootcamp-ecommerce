// @flow
import { nextState } from "./util";

import type {
  BootcampRun,
  PayableRunsResponse,
} from "../../flow/bootcampTypes";

export const bootcampRunsKey = "bootcampRuns";
export const payableRunsEntityKey = "payableRuns";
export const payableRunsQueryKey = payableRunsEntityKey;

export const bootcampRunsSelector = (state: any): ?Array<BootcampRun> =>
  state.entities[bootcampRunsKey];

export default {
  bootcampRunsQuery: () => ({
    queryKey: bootcampRunsKey,
    url: "/api/bootcampruns/?available=true",
    transform: (json: Array<BootcampRun>) => ({
      [bootcampRunsKey]: json,
    }),
    update: {
      [bootcampRunsKey]: nextState,
    },
    force: true,
  }),
  payableBootcampRunsQuery: (username: string) => ({
    queryKey: payableRunsQueryKey,
    url: `/api/v0/bootcamps/${username}/`,
    transform: (json: ?PayableRunsResponse) => ({
      [payableRunsEntityKey]: json,
    }),
    update: {
      [payableRunsEntityKey]: (
        prev: PayableRunsResponse,
        next: PayableRunsResponse,
      ) => next,
    },
    force: true,
  }),
};
