// @flow
/* global SETTINGS:false */
import qs from "query-string"
import { isEmpty, includes, has } from "ramda"

import { routes } from "../lib/urls"

import type { RouterHistory } from "react-router"
import type { AuthResponse, AuthStates } from "../flow/authTypes"

export const FLOW_REGISTER = "register"
export const FLOW_LOGIN = "login"

export const STATE_ERROR = "error"
export const STATE_ERROR_TEMPORARY = "error-temporary"
export const STATE_SUCCESS = "success"
export const STATE_INACTIVE = "inactive"
export const STATE_INVALID_EMAIL = "invalid-email"
export const STATE_USER_BLOCKED = "user-blocked"

export const STATE_LOGIN_EMAIL = "login/email"
export const STATE_LOGIN_PASSWORD = "login/password"
export const STATE_LOGIN_PROVIDER = "login/provider"

export const STATE_REGISTER_EMAIL = "register/email"
export const STATE_REGISTER_CONFIRM_SENT = "register/confirm-sent"
export const STATE_REGISTER_CONFIRM = "register/confirm"
export const STATE_REGISTER_DETAILS = "register/details"
export const STATE_REGISTER_EXTRA_DETAILS = "register/extra"
export const STATE_REGISTER_REQUIRED = "register/required"

export const STATE_REGISTER_BACKEND_EDX = "edxorg"
export const STATE_REGISTER_BACKEND_EMAIL = "email"

export const ALL_STATES = [
  STATE_ERROR,
  STATE_ERROR_TEMPORARY,
  STATE_SUCCESS,
  STATE_INACTIVE,
  STATE_INVALID_EMAIL,
  STATE_USER_BLOCKED,
  STATE_LOGIN_EMAIL,
  STATE_LOGIN_PASSWORD,
  STATE_LOGIN_PROVIDER,
  STATE_REGISTER_EMAIL,
  STATE_REGISTER_CONFIRM,
  STATE_REGISTER_CONFIRM_SENT,
  STATE_REGISTER_DETAILS,
  STATE_REGISTER_EXTRA_DETAILS,
  STATE_REGISTER_REQUIRED
]

export const generateLoginRedirectUrl = () => {
  const { pathname, search, hash } = window.location

  const next = `${pathname}${search}${hash}`
  return `${routes.login.begin}?${qs.stringify({ next })}`
}

export type StateHandlers = {
  [AuthStates]: (response: AuthResponse) => void
}

const getErrorQs = (errors: Array<string>) =>
  !isEmpty(errors) ?
    qs.stringify({
      error: errors[0]
    }) :
    ""

export const handleAuthResponse = (
  history: RouterHistory,
  response: AuthResponse,
  handlers: StateHandlers,
  backend?: string
) => {
  /* eslint-disable camelcase */
  const { state, redirect_url, partial_token, errors, field_errors } = response

  backend = backend || STATE_REGISTER_BACKEND_EDX

  // If a specific handler function was passed in for this response state, invoke it
  if (has(state, handlers)) {
    handlers[state](response)
  }

  if (state === STATE_SUCCESS) {
    window.location = redirect_url || routes.root
  } else if (state === STATE_LOGIN_PASSWORD) {
    history.push(routes.login.password)
  } else if (state === STATE_REGISTER_DETAILS) {
    const params = qs.stringify({
      partial_token,
      backend
    })
    history.push(`${routes.register.details}?${params}`)
  } else if (state === STATE_REGISTER_EXTRA_DETAILS) {
    const params = qs.stringify({
      partial_token,
      backend
    })
    history.push(`${routes.register.extra}?${params}`)
  } else if (state === STATE_USER_BLOCKED) {
    history.push(`${routes.register.denied}?${getErrorQs(errors)}`)
  } else if (
    includes(state, [STATE_ERROR, STATE_ERROR_TEMPORARY]) &&
    isEmpty(field_errors)
  ) {
    // otherwise we're in some kind of error state, explicit or otherwise
    history.push(`${routes.register.error}?${getErrorQs(errors)}`)
  }
  /* eslint-enable camelcase */
}
