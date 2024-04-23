// @flow
import React from "react";
import { path, pathOr, propOr } from "ramda";

import type { ApplicationDetail } from "../flow/applicationTypes";
import type { Country } from "../flow/authTypes";

const formatState = (application: ApplicationDetail) => {
  const stateCode = pathOr(
    "",
    ["user", "legal_address", "state_or_territory"],
    application,
  );
  if (!stateCode) {
    return null;
  }
  const [, statePiece] = stateCode.split("-");
  return `, ${statePiece || stateCode}`;
};

const formatZip = (application: ApplicationDetail) => {
  const zip = path(["user", "legal_address", "postal_code"], application);
  return zip ? (
    <>
      {zip}
      <br />
    </>
  ) : null;
};

const formatCountry = (
  countries: Array<Country>,
  application: ApplicationDetail,
) => {
  const countryCode = path(["user", "legal_address", "country"], application);
  return propOr(
    null,
    "name",
    countries.find((country) => country.code === countryCode),
  );
};

const formatCity = (application: ApplicationDetail) =>
  pathOr(null, ["user", "legal_address", "city"], application);

type Props = {
  application: ApplicationDetail,
  countries: Array<Country>,
};
export default function Address(props: Props) {
  const { application, countries } = props;
  return (
    <>
      {pathOr([], ["user", "legal_address", "street_address"], application).map(
        (address, i) => (
          <div key={i} className="address_field">
            {address}
          </div>
        ),
      )}
      {formatCity(application)}
      {formatState(application)} {formatZip(application)}
      {formatCountry(countries, application)}
    </>
  );
}
