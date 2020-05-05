// @flow
import type { BootcampRunsResponse } from "../../flow/bootcampTypes"

export default {
  bootcampRunQuery: (username: string) => ({
    queryKey:  "bootcampRuns",
    url:       `/api/v0/bootcamps/${username}/`,
    transform: (json: ?BootcampRunsResponse) => ({
      bootcampRuns: json
    }),
    update: {
      bootcampRuns: (prev: BootcampRunsResponse, next: BootcampRunsResponse) =>
        next
    },
    force: true
  })
}
