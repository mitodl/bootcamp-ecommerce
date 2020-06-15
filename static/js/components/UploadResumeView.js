// @flow
/* global SETTINGS: false */
import React from "react"
import Dropzone from "react-dropzone-uploader"
import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync } from "redux-query"
import { values, join, keys } from "ramda"

import applications from "../lib/queries/applications"
import { ErrorMessage, Field, Form, Formik } from "formik"
import FormError from "./forms/elements/FormError"
import { DEFAULT_POST_OPTIONS } from "../lib/redux_query"
import { ALLOWED_FILE_EXTENTIONS } from "../constants"
import type { ApplicationDetail } from "../flow/applicationTypes"

const doneBtnStyle = {
  color:           "#fff",
  backgroundColor: "#dc3545",
  borderColor:     "#d43f3a"
}

type UploaderProps = {
  application: ApplicationDetail
}
export const ResumeUploader = (props: UploaderProps) => {
  const { application } = props

  const getUploadParams = () => {
    return {
      url: `/api/applications/${application.id}/resume/`,
      ...DEFAULT_POST_OPTIONS
    }
  }

  const handleSubmit = (files, allFiles) => {
    allFiles.forEach(f => f.remove())
  }

  const inputContent = () => {
    return (
      <div className="input-label">
        <h3>Drag file here or click to Browse</h3>
        {application.resume_filepath ? (
          <React.Fragment>
            <p className="uploaded-resume">
              Your uploaded resume:{" "}
              <strong>
                {application.resume_filepath.substr(
                  application.resume_filepath.indexOf("_") + 1
                )}
              </strong>
            </p>
            <p>This will replace your existing resume.</p>
          </React.Fragment>
        ) : null}
        <p>Allowed file types: {join(",", keys(ALLOWED_FILE_EXTENTIONS))}</p>
      </div>
    )
  }

  return (
    <Dropzone
      getUploadParams={getUploadParams}
      inputContent={inputContent}
      onSubmit={handleSubmit}
      submitButtonContent="Done"
      classNames="drop-outline"
      maxFiles={1}
      styles={{
        dropzone:     { minHeight: 200, maxHeight: 250 },
        submitButton: doneBtnStyle
      }}
      accept={join(",", values(ALLOWED_FILE_EXTENTIONS))}
    />
  )
}
type Props = {
  application: ?ApplicationDetail,
  uploadResume: (linkedinUrl: string, applicationId: number) => Promise<void>
}

export class UploadResumeView extends React.Component<Props> {
  render() {
    const { uploadResume, application } = this.props

    if (!application) {
      return null
    }
    return (
      <div className="container">
        <div className="drawer-wrapper">
          <h2 className="drawer-title">Resume or LinkedIn Profile</h2>
          <p>Please upload resume or a link to your LinkedIn profile</p>
          <h3>Resume</h3>
          <ResumeUploader application={application} />

          <h3 className="margin-top">LinkedIn URL</h3>
          <Formik
            onSubmit={async ({ linkedinUrl }, actions) => {
              const {
                body: errors
              }: // $FlowFixMe
              { body: Object } = await uploadResume(linkedinUrl, application.id)

              if (errors && errors.length > 0) {
                actions.setErrors({
                  linkedinUrl: errors
                })
              }
              actions.setSubmitting(false)
            }}
            initialValues={{
              linkedinUrl: application.linkedin_url || null
            }}
            render={({ isSubmitting }) => (
              <Form>
                <div className="form-group">
                  <Field
                    name="linkedinUrl"
                    className="form-control"
                    placeholder="LinkedIn URL"
                  />
                  <p className="example-input">
                    Example: https://www.linkedin.com/in/User-Name-7472b48/
                  </p>
                  <ErrorMessage name="linkedinUrl" component={FormError} />
                </div>
                <button
                  className="btn btn-danger"
                  type="submit"
                  disabled={isSubmitting}
                >
                  Submit
                </button>
              </Form>
            )}
          />
        </div>
      </div>
    )
  }
}

const uploadResume = (linkedinUrl: string, applicationId: number) =>
  mutateAsync(
    applications.applicationUploadResumeMutation(linkedinUrl, applicationId)
  )

const mapDispatchToProps = {
  uploadResume: uploadResume
}

export default compose(connect(null, mapDispatchToProps))(UploadResumeView)
