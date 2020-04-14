/* global SETTINGS: false */
import { assert } from "chai"
import fetchMock from "fetch-mock"
import { getCookie, fetchJSONWithCSRF, csrfSafeMethod } from "./api"

describe("api utility functions", function() {
  afterEach(function() {
    for (const cookie of document.cookie.split(";")) {
      const key = cookie.split("=")[0].trim()
      document.cookie = `${key}=`
    }
  })

  describe("fetch functions", () => {
    const CSRF_TOKEN = "asdf"

    afterEach(() => {
      fetchMock.restore()
    })

    describe("fetchJSONWithCSRF", () => {
      it("fetches and populates appropriate headers for JSON", () => {
        document.cookie = `csrftoken=${CSRF_TOKEN}`
        const expectedJSON = { data: true }

        fetchMock.mock("/url", (url, opts) => {
          assert.deepEqual(opts, {
            credentials: "same-origin",
            headers:     {
              Accept:         "application/json",
              "Content-Type": "application/json",
              "X-CSRFToken":  CSRF_TOKEN
            },
            body:   JSON.stringify(expectedJSON),
            method: "PATCH"
          })
          return {
            status: 200,
            body:   '{"json": "here"}'
          }
        })

        return fetchJSONWithCSRF("/url", {
          method: "PATCH",
          body:   JSON.stringify(expectedJSON)
        }).then(responseBody => {
          assert.deepEqual(responseBody, {
            json: "here"
          })
        })
      })

      it("handles responses with no data", () => {
        document.cookie = `csrftoken=${CSRF_TOKEN}`
        const expectedJSON = { data: true }

        fetchMock.mock("/url", (url, opts) => {
          assert.deepEqual(opts, {
            credentials: "same-origin",
            headers:     {
              Accept:         "application/json",
              "Content-Type": "application/json",
              "X-CSRFToken":  CSRF_TOKEN
            },
            body:   JSON.stringify(expectedJSON),
            method: "PATCH"
          })
          return {
            status: 200,
            body:   ""
          }
        })

        return fetchJSONWithCSRF("/url", {
          method: "PATCH",
          body:   JSON.stringify(expectedJSON)
        }).then(responseBody => {
          assert.deepEqual(responseBody, "")
        })
      })

      for (const statusCode of [300, 400, 500]) {
        it(`rejects the promise if the status code is ${statusCode}`, () => {
          fetchMock.mock("/url", {
            status: statusCode,
            body:   JSON.stringify({
              error: "an error"
            })
          })

          return assert
            .isRejected(fetchJSONWithCSRF("/url"))
            .then(responseBody => {
              assert.deepEqual(responseBody, {
                error:           "an error",
                errorStatusCode: statusCode
              })
            })
        })
      }
    })
  })

  describe("getCookie", () => {
    it("gets a cookie", () => {
      document.cookie = "key=cookie"
      assert.equal("cookie", getCookie("key"))
    })

    it("handles multiple cookies correctly", () => {
      document.cookie = "key1=cookie1"
      document.cookie = "key2=cookie2"
      assert.equal("cookie1", getCookie("key1"))
      assert.equal("cookie2", getCookie("key2"))
    })
    it("returns null if cookie not found", () => {
      assert.equal(null, getCookie("unknown"))
    })
  })

  describe("csrfSafeMethod", () => {
    it("knows safe methods", () => {
      for (const method of ["GET", "HEAD", "OPTIONS", "TRACE"]) {
        assert.ok(csrfSafeMethod(method))
      }
    })
    it("knows unsafe methods", () => {
      for (const method of ["PATCH", "PUT", "DELETE", "POST"]) {
        assert.ok(!csrfSafeMethod(method))
      }
    })
  })
})
