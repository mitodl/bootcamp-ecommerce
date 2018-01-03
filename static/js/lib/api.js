// @flow
/* global SETTINGS:false, fetch: false */
// For mocking purposes we need to use 'fetch' defined as a global instead of importing as a local.
import "isomorphic-fetch"
import R from "ramda"

export function getCookie(name: string): string | null {
  let cookieValue = null

  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")

    for (let cookie of cookies) {
      cookie = cookie.trim()

      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === `${name}=`) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export function csrfSafeMethod(method: string): boolean {
  // these HTTP methods do not require CSRF protection
  return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
}

const headers = R.merge({ headers: {} })

const method = R.merge({ method: "GET" })

const credentials = R.merge({ credentials: "same-origin" })

const setWith = R.curry((path, valFunc, obj) => R.set(path, valFunc(), obj))

const csrfToken = R.unless(
  R.compose(csrfSafeMethod, R.prop("method")),
  setWith(R.lensPath(["headers", "X-CSRFToken"]), () => getCookie("csrftoken"))
)

const jsonHeaders = R.merge({
  headers: {
    "Content-Type": "application/json",
    Accept:         "application/json"
  }
})

const formatRequest = R.compose(csrfToken, credentials, method, headers)

const formatJSONRequest = R.compose(formatRequest, jsonHeaders)

/**
 * Calls to fetch but does a few other things:
 *  - turn cookies on for this domain
 *  - set headers to handle JSON properly
 *  - handle CSRF
 *  - non 2xx status codes will reject the promise returned
 *  - response JSON is returned in place of response
 */
export const fetchJSONWithCSRF = (
  input: string,
  init: Object = {},
  loginOnError: boolean = false
): Promise<*> => {
  return fetch(input, formatJSONRequest(init))
    .then(response => {
      // Not using response.json() here since it doesn't handle empty responses
      // Also note that text is a promise here, not a string
      const text = response.text()

      // For 400 and 401 errors, force login
      // the 400 error comes from edX in case there are problems with the refresh
      // token because the data stored locally is wrong and the solution is only
      // to force a new login
      if (
        loginOnError === true &&
        (response.status === 400 || response.status === 401)
      ) {
        const relativePath = window.location.pathname + window.location.search
        const loginRedirect = `/login/edxorg/?next=${encodeURIComponent(
          relativePath
        )}`
        window.location = `/logout?next=${encodeURIComponent(loginRedirect)}`
      }

      // For non 2xx status codes reject the promise adding the status code
      if (response.status < 200 || response.status >= 300) {
        return text.then(text => {
          return Promise.reject([text, response.status])
        })
      }

      return text
    })
    .then(text => {
      if (text.length !== 0) {
        return JSON.parse(text)
      } else {
        return ""
      }
    })
    .catch(([text, statusCode]) => {
      let respJson = {}
      if (text.length !== 0) {
        try {
          respJson = JSON.parse(text)
        } catch (e) {
          // If the JSON.parse raises, it means that the backend sent a JSON invalid
          // string, and in this context the content received is not important
          // and can be discarded
        }
      }
      respJson.errorStatusCode = statusCode
      return Promise.reject(respJson)
    })
}
