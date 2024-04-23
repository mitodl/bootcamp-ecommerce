// @flow
import React from "react";
import { Formik, Form } from "formik";

import { profileValidation } from "../../lib/validation";
import { ProfileFields } from "./ProfileFormFields";
import ButtonWithLoader from "../loaders/ButtonWithLoader";

type Props = {
  onSubmit: Function,
};

const INITIAL_VALUES = {
  profile: {
    birth_year: "",
    gender: "",
    company: "",
    job_title: "",
    job_function: "",
    industry: "",
    company_size: "",
    years_experience: "",
    highest_education: "",
  },
};

const RegisterExtraDetailsForm = ({ onSubmit }: Props) => (
  <Formik
    onSubmit={onSubmit}
    validationSchema={profileValidation}
    initialValues={INITIAL_VALUES}
    render={({ isSubmitting }) => (
      <Form>
        <ProfileFields />
        <div>
          <div className="required">*=Required</div>
          <div className="row submit-row no-gutters justify-content-end">
            <ButtonWithLoader
              type="submit"
              className="btn btn-outline-danger large-font"
              loading={isSubmitting}
            >
              Continue
            </ButtonWithLoader>
          </div>
        </div>
      </Form>
    )}
  />
);

export default RegisterExtraDetailsForm;
