// @flow
/* global SETTINGS:false */
import React from "react";

import { Formik, Field, Form, ErrorMessage } from "formik";

import { PasswordInput } from "./elements/inputs";
import FormError from "./elements/FormError";
import { resetPasswordFormValidation } from "../../lib/validation";
import ButtonWithLoader from "../loaders/ButtonWithLoader";

type Props = {
  onSubmit: Function,
};

export type ResetPasswordFormValues = {
  newPassword: string,
  confirmPassword: string,
};

const ResetPasswordForm = ({ onSubmit }: Props) => (
  <Formik
    onSubmit={onSubmit}
    validationSchema={resetPasswordFormValidation}
    initialValues={{
      newPassword: "",
      reNewPassword: "",
    }}
    render={({ isSubmitting }) => (
      <Form>
        <div className="form-group">
          <label htmlFor="newPassword">New Password</label>
          <Field
            name="newPassword"
            className="form-control"
            component={PasswordInput}
          />
          <ErrorMessage name="newPassword" component={FormError} />
        </div>
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <Field
            name="confirmPassword"
            className="form-control"
            component={PasswordInput}
          />
          <ErrorMessage name="confirmPassword" component={FormError} />
        </div>
        <div className="row submit-row no-gutters justify-content-end">
          <ButtonWithLoader
            type="submit"
            className="btn btn-danger large-font"
            loading={isSubmitting}
          >
            Submit
          </ButtonWithLoader>
        </div>
      </Form>
    )}
  />
);

export default ResetPasswordForm;
