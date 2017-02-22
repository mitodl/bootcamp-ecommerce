/* global SETTINGS:false, fetch: false */
// For mocking purposes we need to use 'fetch' defined as a global instead of importing as a local.
import 'isomorphic-fetch';
import _ from 'lodash';

export function getCookie(name) {
  let cookieValue = null;

  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');

    for (let cookie of cookies) {
      cookie = cookie.trim();

      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === `${name}=`) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
}

/**
 * Calls to fetch but does a few other things:
 *  - turn cookies on for this domain
 *  - set headers to handle JSON properly
 *  - handle CSRF
 *  - non 2xx status codes will reject the promise returned
 *  - response JSON is returned in place of response
 *
 * @param {string} input URL of fetch
 * @param {Object} init Settings to pass to fetch
 * @param {bool} loginOnError force login on http errors
 * @returns {Promise} The promise with JSON of the response
 */
export function fetchJSONWithCSRF(input, init, loginOnError) {
  if (init === undefined) {
    init = {};
  }
  if (loginOnError === undefined) {
    loginOnError = false;
  }
  init.headers = init.headers || {};
  _.defaults(init.headers, {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  });

  let method = init.method || 'GET';

  if (!csrfSafeMethod(method)) {
    init.headers['X-CSRFToken'] = getCookie('csrftoken');
  }
  // turn on cookies for this domain
  init.credentials = 'same-origin';

  return fetch(input, init).then(response => {
    // Not using response.json() here since it doesn't handle empty responses
    // Also note that text is a promise here, not a string
    let text = response.text();

    // For 400 and 401 errors, force login
    // the 400 error comes from edX in case there are problems with the refresh
    // token because the data stored locally is wrong and the solution is only
    // to force a new login
    if (loginOnError === true && (response.status === 400 || response.status === 401)) {
      window.location = '/login/edxorg/';
    }
    // For non 2xx status codes reject the promise
    if (response.status < 200 || response.status >= 300) {
      return Promise.reject(text);
    }
    return text;
  }).then(text => {
    if (text.length !== 0) {
      return JSON.parse(text);
    } else {
      return "";
    }
  });
}

// import to allow mocking in tests
import { fetchJSONWithCSRF as mockableFetchJSONWithCSRF } from './api';
export function patchThing(username, newThing) {
  return mockableFetchJSONWithCSRF(`/api/v0/thing/${username}/`, {
    method: 'PATCH',
    body: JSON.stringify(newThing)
  });
}
