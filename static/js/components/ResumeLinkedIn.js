// @flow
/* global SETTINGS: false */
import React from "react"
import { compose } from "redux"
import { connect } from "react-redux"
import { mutateAsync, requestAsync } from "redux-query"
import Dropzone from "react-dropzone-uploader"
import { values, join, keys } from "ramda"
import { ErrorMessage, Field, Form, Formik, FormikActions } from "formik"
import * as yup from "yup"

import SupportLink from "./SupportLink"
import FormError from "./forms/elements/FormError"
import { closeDrawer } from "../reducers/drawer"
import applications, {
  applicationDetailSelector
} from "../lib/queries/applications"
import { DEFAULT_NON_GET_OPTIONS } from "../lib/redux_query"
import queries from "../lib/queries"
import {
  getFilenameFromMediaPath,
  getFirstResponseBodyError,
  isErrorResponse,
  isNilOrBlank
} from "../util/util"
import { appResumeAPI } from "../lib/urls"
import { ALLOWED_FILE_EXTENSIONS } from "../constants"

import type {
  ApplicationDetail,
  ResumeLinkedInResponse
} from "../flow/applicationTypes"

type UploaderProps = {
  application: ApplicationDetail,
  resumeFilename: ?string,
  onSuccessfulUpload: Function
}

export const ResumeUploader = (props: UploaderProps) => {
  const { application, resumeFilename, onSuccessfulUpload } = props

  const onChangeStatus = async (fileWithMeta, status) => {
    if (status === "done") {
      await onSuccessfulUpload()
    }
  }

  const onSubmit = (files, allFiles) => {
    allFiles.forEach(f => f.remove())
  }

  const inputContent = (
    <div>
      Drag Files or Click to Browse.
      <br />
      <span className="file-types">
        Allowed file types: {join(",", keys(ALLOWED_FILE_EXTENSIONS))}
      </span>
    </div>
  )

  return (
    <React.Fragment>
      <Dropzone
        getUploadParams={() => ({
          url: appResumeAPI.param({ applicationId: application.id }).toString(),
          ...DEFAULT_NON_GET_OPTIONS
        })}
        onChangeStatus={onChangeStatus}
        onSubmit={onSubmit}
        submitButtonContent="Done"
        inputContent={inputContent}
        classNames="drop-outline"
        maxFiles={1}
        styles={{
          dropzone: { minHeight: 200, maxHeight: 250 }
        }}
        accept={join(",", values(ALLOWED_FILE_EXTENSIONS))}
      />
      {!isNilOrBlank(resumeFilename) && (
        <p className="uploaded">
          Your uploaded resume: <strong>{resumeFilename}</strong>
        </p>
      )}
    </React.Fragment>
  )
}

export const resumeLinkedInValidation = yup.object().shape({
  linkedInUrl: yup
    .string()
    .label("LinkedIn URL")
    .trim()
    .url()
    .when("resumeFilename", (resumeFilename, schema) => {
      if (isNilOrBlank(resumeFilename)) {
        return schema.required("A resume or a LinkedIn URL must be provided.")
      }
    })
})

type ResumeLinkedInForm = {
  linkedInUrl: string,
  resumeFilename: string
}

type Props = {
  application: ?ApplicationDetail,
  closeDrawer: () => void,
  fetchAppDetail: (applicationId: string, force: boolean) => Promise<void>,
  addLinkedInUrl: (
    applicationId: number,
    linkedInUrl: string
  ) => Promise<ResumeLinkedInResponse>
}

export class ResumeLinkedIn extends React.Component<Props> {
  onFormSubmit = async (
    { linkedInUrl, resumeFilename }: ResumeLinkedInForm,
    actions: FormikActions<*>
  ) => {
    const { application, addLinkedInUrl, closeDrawer } = this.props

    if (!application) {
      return
    }

    if (resumeFilename !== "" && linkedInUrl === "") {
      actions.resetForm()
      closeDrawer()
      return
    }

    const linkedInResponse = await addLinkedInUrl(application.id, linkedInUrl)

    if (isErrorResponse(linkedInResponse)) {
      const responseBodyError = getFirstResponseBodyError(linkedInResponse)
      actions.setErrors({
        linkedInUrl: responseBodyError || (
          <span>
            Something went wrong while adding your LinkedIn profile. Please try
            again, or <SupportLink />
          </span>
        )
      })
      actions.setSubmitting(false)
    } else {
      actions.resetForm()
      closeDrawer()
    }
  }

  handleSuccessfulUpload = async () => {
    const { application, fetchAppDetail } = this.props

    if (!application) {
      return
    }

    // HACK: react-dropzone-uploader does not yet provide a way to access the
    // server response after a successful upload. To get around this, we make
    // another request for the application detail to "refresh" that data and get
    // the up-to-date resume.
    await fetchAppDetail(String(application.id), true)
  }

  render() {
    const { application } = this.props

    if (!application) {
      return null
    }

    const resumeFilename = getFilenameFromMediaPath(application.resume_url)
    const initialFormValues: ResumeLinkedInForm = {
      linkedInUrl:    application.linkedin_url || "",
      resumeFilename: resumeFilename
    }

    return (
      <div className="container drawer-wrapper resume-linkedin-drawer">
        <h2>Resume or LinkedIn Profile</h2>
        <p>Please upload resume or a link to your LinkedIn profile</p>
        <h3>Resume</h3>
        <ResumeUploader
          application={application}
          resumeFilename={resumeFilename}
          onSuccessfulUpload={this.handleSuccessfulUpload}
        />

        <h3 className="mt-5">LinkedIn URL</h3>
        <Formik
          onSubmit={this.onFormSubmit}
          validationSchema={resumeLinkedInValidation}
          initialValues={initialFormValues}
          enableReinitialize={true}
          validateOnChange={true}
          validateOnBlur={false}
          render={({ isSubmitting }) => (
            <Form>
              <div className="form-group">
                <Field
                  name="linkedInUrl"
                  className="form-control"
                  placeholder="LinkedIn URL"
                />
                <div className="caption bottom">
                  Example: https://www.linkedin.com/in/User-Name-7472b48/
                </div>
                <ErrorMessage name="linkedInUrl" component={FormError} />
              </div>
              <button
                className="btn-danger"
                type="submit"
                disabled={isSubmitting}
              >
                Submit
              </button>
            </Form>
          )}
        />
      </div>
    )
  }
}

const mapStateToProps = (state, ownProps) => ({
  application: applicationDetailSelector(ownProps.applicationId, state)
})

const mapDispatchToProps = dispatch => ({
  closeDrawer:    () => dispatch(closeDrawer()),
  addLinkedInUrl: async (
    applicationId: number,
    linkedInUrl: string
  ): Promise<ResumeLinkedInResponse> =>
    dispatch(
      mutateAsync(
        applications.applicationLinkedInUrlMutation(applicationId, linkedInUrl)
      )
    ),
  fetchAppDetail: async (applicationId: string, force: ?boolean) =>
    dispatch(
      requestAsync(
        queries.applications.applicationDetailQuery(
          String(applicationId),
          !!force
        )
      )
    )
})

export default compose(connect(mapStateToProps, mapDispatchToProps))(
  ResumeLinkedIn
)
