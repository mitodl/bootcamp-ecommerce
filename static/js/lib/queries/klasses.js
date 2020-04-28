// @flow
import type { KlassesResponse } from "../../flow/klassTypes"

export default {
  klassQuery: (username: string) => ({
    queryKey:  "klasses",
    url:       `/api/v0/klasses/${username}/`,
    transform: (json: ?KlassesResponse) => ({
      klasses: json
    }),
    update: {
      klasses: (prev: KlassesResponse, next: KlassesResponse) => next
    },
    force: true
  })
}
