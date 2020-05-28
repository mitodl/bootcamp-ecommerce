// @flow
import type {BootcampRun} from "./bootcampTypes"

export type Application = {
  id:           number,
  state:        string,
  created_on:   any,
  bootcamp_run: BootcampRun
}
