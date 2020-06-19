import { fromPairs } from "ramda"
import {
  EMPLOYMENT_EXPERIENCE,
  EMPLOYMENT_SIZE,
  GENDER_CHOICES
} from "../constants"
import React from "react"

import type { User } from "../flow/authTypes"

type Props = {
  user: User
}

export default function UserDetails(props: Props) {
  const { user } = props
  return (
    <div className="profile-display">
      <div className="row profile-row">
        <div className="col profile-label">First Name</div>
        <div className="col">{user.legal_address.first_name}</div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Last Name</div>
        <div className="col">{user.legal_address.last_name}</div>
      </div>
      {user.legal_address.street_address.map((line, idx) => (
        <div className="row profile-row" key={idx}>
          <div className="col profile-label">
            Address{idx > 0 && ` ${idx + 1}`}
          </div>
          <div className="col">{line}</div>
        </div>
      ))}
      {user.legal_address.country ? (
        <div className="row profile-row">
          <div className="col profile-label">Country</div>
          <div className="col">{user.legal_address.country}</div>
        </div>
      ) : null}
      <div className="row profile-row">
        <div className="col profile-label">City</div>
        <div className="col">{user.legal_address.city}</div>
      </div>
      {user.legal_address.state_or_territory ? (
        <div className="row profile-row">
          <div className="col profile-label">State/Province/Region</div>
          <div className="col">{user.legal_address.state_or_territory}</div>
        </div>
      ) : null}
      <div className="divider" />
      <div className="row profile-row">
        <div className="col profile-label">Gender</div>
        <div className="col">
          {fromPairs(GENDER_CHOICES)[user.profile.gender]}
        </div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Year of Birth</div>
        <div className="col">{user.profile.birth_year}</div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Company</div>
        <div className="col">{user.profile.company}</div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Job Title</div>
        <div className="col">{user.profile.job_title}</div>
      </div>
      <div className="form-group dotted" />
      <div className="row profile-row">
        <div className="col profile-label">Industry</div>
        <div className="col">{user.profile.industry}</div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Job Function</div>
        <div className="col">{user.profile.job_function}</div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Company Size</div>
        <div className="col">
          {fromPairs(EMPLOYMENT_SIZE)[user.profile.company_size]}
        </div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Years of Work Experience</div>
        <div className="col">
          {fromPairs(EMPLOYMENT_EXPERIENCE)[user.profile.years_experience]}
        </div>
      </div>
      <div className="row profile-row">
        <div className="col profile-label">Highest Level of Education</div>
        <div className="col">{user.profile.highest_education}</div>
      </div>
    </div>
  )
}
