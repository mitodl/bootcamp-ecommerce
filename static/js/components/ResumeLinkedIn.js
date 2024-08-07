// @flow
/* global SETTINGS: false */
import React from "react";
import { compose } from "redux";
import { connect } from "react-redux";
import { mutateAsync, requestAsync } from "redux-query";
import Dropzone, {
  formatBytes,
  formatDuration,
} from "@mitodl/react-dropzone-uploader";
import { values, join, keys } from "ramda";
import { ErrorMessage, Field, Form, Formik, FormikActions } from "formik";
import * as yup from "yup";

import SupportLink from "./SupportLink";
import ButtonWithLoader from "./loaders/ButtonWithLoader";
import FormError from "./forms/elements/FormError";
import { closeDrawer } from "../reducers/drawer";
import applications, {
  applicationDetailSelector,
} from "../lib/queries/applications";
import { DEFAULT_NON_GET_OPTIONS } from "../lib/redux_query";
import queries from "../lib/queries";
import {
  getFilenameFromMediaPath,
  getFirstResponseBodyError,
  getXhrResponseError,
  isErrorResponse,
  isNilOrBlank,
} from "../util/util";
import { appResumeAPI } from "../lib/urls";
import {
  ALLOWED_FILE_EXTENSIONS,
  DEFAULT_MAX_RESUME_FILE_SIZE,
} from "../constants";

import type {
  ApplicationDetail,
  ResumeLinkedInResponse,
} from "../flow/applicationTypes";
import type IPreviewProps from "@mitodl/react-dropzone-uploader";

type UploaderProps = {
  application: ApplicationDetail,
  resumeFilename: ?string,
  onSuccessfulUpload: Function,
};

const defaultUploadErrorText = "Your file failed to upload.";

/*
 * Custom component to pass to react-dropzone-uploader. Used to display the file being uploaded, progress bar, and
 * error messages.
 */
class CustomPreview extends React.PureComponent<IPreviewProps> {
  render() {
    const {
      className,
      imageClassName,
      style,
      imageStyle,
      fileWithMeta: {
        cancel,
        remove,
        restart,
        meta: { response },
      },
      meta: {
        name = "",
        percent = 0,
        size = 0,
        previewUrl,
        status,
        duration,
        validationError,
      },
      isUpload,
      canCancel,
      canRemove,
      canRestart,
      extra: { minSizeBytes },
    } = this.props;

    let fileNameDisplay = `${name || "?"}, ${formatBytes(size)}`;
    if (duration) {
      fileNameDisplay = `${fileNameDisplay}, ${formatDuration(duration)}`;
    }
    let errorText = null;

    if (status === "error_file_size" || status === "error_validation") {
      if (status === "error_file_size") {
        errorText = size < minSizeBytes ? "File too small" : "File too large";
      } else if (status === "error_validation") {
        errorText = String(validationError);
      }
    }

    if (
      status === "error_upload_params" ||
      status === "exception_upload" ||
      status === "error_upload"
    ) {
      errorText = getXhrResponseError(response) || defaultUploadErrorText;
    } else if (status === "aborted") {
      errorText = "Cancelled";
    }

    return (
      <div className={className} style={style}>
        {previewUrl && (
          <img
            className={imageClassName}
            style={imageStyle}
            src={previewUrl}
            alt={fileNameDisplay}
            title={fileNameDisplay}
          />
        )}
        {!previewUrl && (
          <span className="dzu-previewFileName">{fileNameDisplay}</span>
        )}

        <div className="dzu-previewStatusContainer">
          {isUpload && !errorText && (
            <progress
              max={100}
              value={
                status === "done" || status === "headers_received"
                  ? 100
                  : percent
              }
            />
          )}
        </div>
        {status === "uploading" && canCancel && (
          <button className="borderless" onClick={cancel}>
            <i className="material-icons" onClick={cancel}>
              close
            </i>
          </button>
        )}
        {!["preparing", "getting_upload_params", "uploading", "done"].includes(
          status,
        ) &&
          canRemove && (
            <button className="borderless" onClick={remove}>
              <i className="material-icons" onClick={remove}>
                close
              </i>
            </button>
          )}
        {status === "done" && canRemove && (
          <button className="borderless" onClick={remove}>
            <i className="material-icons" onClick={remove}>
              check
            </i>
          </button>
        )}
        {[
          "error_upload_params",
          "exception_upload",
          "error_upload",
          "aborted",
          "ready",
        ].includes(status) &&
          canRestart && (
            <button className="borderless" onClick={restart}>
              <i className="material-icons">refresh</i>
            </button>
          )}
        {errorText && <div className="error text-left">{errorText}</div>}
      </div>
    );
  }
}

export const ResumeUploader = (props: UploaderProps) => {
  const { application, resumeFilename, onSuccessfulUpload } = props;

  const onChangeStatus = async (fileWithMeta, status) => {
    if (status === "done") {
      await onSuccessfulUpload();
    }
  };

  const onSubmit = (files, allFiles) => {
    allFiles.forEach((f) => f.remove());
  };

  const inputContent = (
    // This key is needed to avoid a warning in react-dropzone-uploader
    <div key="input-content">
      Drag Files or Click to Browse.
      <br />
      <span className="file-types">
        Allowed file types: {join(",", keys(ALLOWED_FILE_EXTENSIONS))}
      </span>
    </div>
  );

  return (
    <React.Fragment>
      <Dropzone
        getUploadParams={() => ({
          url: appResumeAPI.param({ applicationId: application.id }).toString(),
          ...DEFAULT_NON_GET_OPTIONS,
        })}
        onChangeStatus={onChangeStatus}
        onSubmit={onSubmit}
        submitButtonContent="Done"
        inputContent={inputContent}
        classNames="drop-outline"
        maxFiles={1}
        styles={{
          dropzone: { minHeight: 200, maxHeight: 250 },
        }}
        accept={join(",", values(ALLOWED_FILE_EXTENSIONS))}
        maxSizeBytes={SETTINGS.upload_max_size || DEFAULT_MAX_RESUME_FILE_SIZE}
        PreviewComponent={CustomPreview}
      />
      {!isNilOrBlank(resumeFilename) && (
        <p className="uploaded">
          Your uploaded resume: <strong>{resumeFilename}</strong>
        </p>
      )}
    </React.Fragment>
  );
};

export const resumeLinkedInValidation = yup.object().shape({
  linkedInUrl: yup
    .string()
    .label("LinkedIn URL")
    .trim()
    .url()
    .max(200, "The URL should be less than 200 characters.")
    .lowercase()
    .matches(
      "^(http|https)://([a-zA-Z]{2,3}[.]|)linkedin[.]([a-zA-Z]{2,3})/+([a-zA-Z0-9-_])+/+([a-zA-Z0-9-_])+.*$",
      "Please enter a valid LinkedIn URL",
    )
    .when("resumeFilename", (resumeFilename, schema) => {
      if (isNilOrBlank(resumeFilename)) {
        return schema.required("A resume or a LinkedIn URL must be provided.");
      }
    }),
});

type ResumeLinkedInForm = {
  linkedInUrl: string,
  resumeFilename: string,
};

type Props = {
  application: ?ApplicationDetail,
  closeDrawer: () => void,
  fetchAppDetail: (applicationId: string, force: boolean) => Promise<void>,
  addLinkedInUrl: (
    applicationId: number,
    linkedInUrl: string,
  ) => Promise<ResumeLinkedInResponse>,
};

export class ResumeLinkedIn extends React.Component<Props> {
  onFormSubmit = async (
    { linkedInUrl, resumeFilename }: ResumeLinkedInForm,
    actions: FormikActions<*>,
  ) => {
    const { application, addLinkedInUrl, closeDrawer } = this.props;

    if (!application) {
      return;
    }

    if (resumeFilename !== "" && linkedInUrl === "") {
      actions.resetForm();
      closeDrawer();
      return;
    }

    const linkedInResponse = await addLinkedInUrl(application.id, linkedInUrl);

    if (isErrorResponse(linkedInResponse)) {
      const responseBodyError = getFirstResponseBodyError(linkedInResponse);
      actions.setErrors({
        linkedInUrl: responseBodyError || (
          <span>
            Something went wrong while adding your LinkedIn profile. Please try
            again, or <SupportLink />
          </span>
        ),
      });
      actions.setSubmitting(false);
    } else {
      actions.resetForm();
      closeDrawer();
    }
  };

  handleSuccessfulUpload = async () => {
    const { application, fetchAppDetail } = this.props;

    if (!application) {
      return;
    }

    // HACK: react-dropzone-uploader does not yet provide a way to access the
    // server response after a successful upload. To get around this, we make
    // another request for the application detail to "refresh" that data and get
    // the up-to-date resume.
    await fetchAppDetail(String(application.id), true);
  };

  render() {
    const { application } = this.props;

    if (!application) {
      return null;
    }

    const resumeFilename = getFilenameFromMediaPath(application.resume_url);
    const initialFormValues: ResumeLinkedInForm = {
      linkedInUrl: application.linkedin_url || "",
      resumeFilename: resumeFilename,
    };

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
              <ButtonWithLoader
                className="btn-danger"
                type="submit"
                loading={isSubmitting}
              >
                Submit
              </ButtonWithLoader>
            </Form>
          )}
        />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  application: applicationDetailSelector(ownProps.applicationId, state),
});

const mapDispatchToProps = (dispatch) => ({
  closeDrawer: () => dispatch(closeDrawer()),
  addLinkedInUrl: async (
    applicationId: number,
    linkedInUrl: string,
  ): Promise<ResumeLinkedInResponse> =>
    dispatch(
      mutateAsync(
        applications.applicationLinkedInUrlMutation(applicationId, linkedInUrl),
      ),
    ),
  fetchAppDetail: async (applicationId: string, force: ?boolean) =>
    dispatch(
      requestAsync(
        queries.applications.applicationDetailQuery(
          String(applicationId),
          !!force,
        ),
      ),
    ),
});

export default compose(connect(mapStateToProps, mapDispatchToProps))(
  ResumeLinkedIn,
);
