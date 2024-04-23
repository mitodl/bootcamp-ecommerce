// @flow
import type { HttpResponse } from "./httpTypes";

// API response types

export type AuthStates =
  | "success"
  | "inactive"
  | "invalid-email"
  | "user-blocked"
  | "error"
  | "login/email"
  | "login/password"
  | "login/backend"
  | "register/email"
  | "register/confirm-sent"
  | "register/confirm"
  | "register/details"
  | "register/extra"
  | "register/required"
  | "register/retry";

export type AuthFlow = "register" | "login";

export type AuthErrors = Array<string>;

export type AuthFieldErrors = {
  [string]: string,
};

export type AuthResponse = {
  partial_token: ?string,
  flow: AuthFlow,
  backend: string,
  state: AuthStates,
  errors: AuthErrors,
  field_errors: AuthFieldErrors,
  redirect_url: ?string,
  extra_data: Object,
};

export type PartialProfile = {
  name: string,
};

export type LegalAddress = {
  first_name: string,
  last_name: string,
  street_address: Array<string>,
  country: string,
  state_or_territory?: string,
  postal_code?: string,
  is_complete: boolean,
};

export type Profile = {
  name: ?string,
  gender: string,
  birth_year: number,
  company: string,
  industry: ?string,
  job_title: string,
  job_function: ?string,
  years_experience: ?number,
  company_size: ?number,
  highest_education: ?string,
  is_complete: boolean,
  updated_on: string,
  can_skip_application_steps: boolean,
};

export type User = {
  id: number,
  username: string,
  email: string,
  name: string,
  created_on: string,
  updated_on: string,
  profile: ?Profile,
  legal_address: ?LegalAddress,
};

export type AnonymousUser = {
  is_anonymous: true,
  is_authenticated: false,
};

export type LoggedInUser = {
  is_anonymous: false,
  is_authenticated: true,
} & User;

export type CurrentUser = AnonymousUser | LoggedInUser;

export type HttpAuthResponse<T> = {
  body: T | Object,
  status: number,
};

export type StateOrTerritory = {
  name: string,
  code: string,
};

export type Country = {
  name: string,
  code: string,
  states: Array<StateOrTerritory>,
};

export type ProfileForm = {
  profile: Profile,
};

export type EmailFormValues = {
  email: string,
};

export type PasswordFormValues = {
  password: string,
};

export type UserProfileForm = {
  email: string,
  name: string,
  legal_address: ?LegalAddress,
  profile: ?Profile,
};

export type updateEmailResponse = {
  confirmed: boolean,
  detail: ?string,
};

export type EditProfileResponse = HttpResponse<User>;
