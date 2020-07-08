// @flow
import React, { useCallback } from "react"
import qs from "query-string"
import urljoin from "url-join"
import { prop, omit } from "ramda"
import { useLocation, useHistory } from "react-router"
import { identity } from "ramda"

import {
  STATUS_FACET_KEY,
  BOOTCAMP_FACET_KEY,
  FACET_DISPLAY_NAMES,
  FACET_OPTION_LABEL_KEYS,
  FACET_ORDER,
  REVIEW_STATUS_DISPLAY_MAP
} from "../constants"

import type { FacetOption, SubmissionFacetData } from "../flow/applicationTypes"

export const facetOptionSerialization = {
  [STATUS_FACET_KEY]: {
    qsKey:      "review_status",
    getQSValue: prop("review_status")
  },
  [BOOTCAMP_FACET_KEY]: {
    qsKey:      "bootcamp_id",
    getQSValue: prop("id")
  }
}

export const facetOptionLabels = {
  [STATUS_FACET_KEY]:   status => REVIEW_STATUS_DISPLAY_MAP[status][0],
  [BOOTCAMP_FACET_KEY]: identity
}

type OptionProps = {
  option: FacetOption,
  facetKey: string
}

export function Option({ option, facetKey }: OptionProps) {
  const labelKey = FACET_OPTION_LABEL_KEYS[facetKey]
  const { qsKey, getQSValue } = facetOptionSerialization[facetKey]

  const location = useLocation()
  const history = useHistory()

  const facetIsActive =
    qs.parse(location.search)[qsKey] === String(getQSValue(option))

  const cb = useCallback(
    e => {
      e.preventDefault()

      let updatedParams = facetIsActive ?
        omit([qsKey], qs.parse(location.search)) :
        {
          ...qs.parse(location.search),
          [qsKey]: getQSValue(option)
        }
      updatedParams = omit(["limit", "offset"], updatedParams)
      const url = urljoin(location.pathname, `/?${qs.stringify(updatedParams)}`)
      history.push(url)
    },
    [option, facetKey, location]
  )

  const className = `facet-option my-3 ${
    facetIsActive ? "font-weight-bold" : ""
  }`.trim()

  return (
    <div className={className} onClick={cb}>
      {facetOptionLabels[facetKey](option[labelKey])}
    </div>
  )
}

type Props = {
  facets: SubmissionFacetData
}

export default function SubmissionFacets({ facets }: Props) {
  return (
    <div className="submission-facets">
      {FACET_ORDER.map((facetKey, i) => (
        <div className="facet mb-4" key={i}>
          <h3 className="title font-weight-bold">
            {FACET_DISPLAY_NAMES[facetKey]}
          </h3>
          {facets[facetKey].map((option, i) => (
            <Option option={option} key={i} facetKey={facetKey} />
          ))}
        </div>
      ))}
    </div>
  )
}
