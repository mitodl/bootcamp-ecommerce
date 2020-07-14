import { assert } from "chai"

import * as api from "./applicationApi"
import {
  makeApplication,
  makeApplicationDetail
} from "../factories/application"
import { generateOrder } from "../factories"
import { ORDER_STATUS_FAILED, ORDER_STATUS_FULFILLED } from "../constants"

describe("applications API", () => {
  it("calcOrderBalances sorts orders by updated_on and balances from the application", () => {
    const application = makeApplicationDetail()
    application.price = 60
    // $FlowFixMe
    application.orders = [
      { ...generateOrder(), total_price_paid: 20, updated_on: "2020-01-01" },
      { ...generateOrder(), total_price_paid: 30, updated_on: "2020-02-01" }
    ]
    const {
      ordersAndBalances,
      totalPaid,
      totalPrice,
      balanceRemaining
    } = api.calcOrderBalances(application)
    assert.deepEqual(ordersAndBalances, [
      {
        order:   application.orders[0],
        balance: 40
      },
      {
        order:   application.orders[1],
        balance: 10
      }
    ])
    assert.equal(totalPaid, 50)
    assert.equal(totalPrice, 60)
    assert.equal(balanceRemaining, 10)
  })

  //
  ;[
    [400, ORDER_STATUS_FULFILLED, "response indicates error", true],
    [200, null, "response body is empty", false],
    [200, "pending", "order status indicates that it's still pending", false],
    [200, ORDER_STATUS_FULFILLED, "order status is fulfilled", true],
    [200, ORDER_STATUS_FAILED, "order status is failed", true]
  ].forEach(([statusCode, statusText, desc, expected]) => {
    it(`isStatusPollingFinished should return ${String(
      expected
    )} when ${desc}`, () => {
      const responseBody = statusText ?
        {
          body: {
            status: statusText
          }
        } :
        {}
      const response = {
        status: statusCode,
        ...responseBody
      }
      assert.equal(api.isStatusPollingFinished(response), expected)
    })
  })

  it("findAppByRunTitle should return an application matching a given bootcamp run title", () => {
    const applications = [makeApplication(), makeApplication()]
    const titleToSearch = `My Title: ${applications[0].bootcamp_run.title}`
    assert.isNotOk(api.findAppByRunTitle(applications, titleToSearch))
    applications[0].bootcamp_run.title = titleToSearch
    assert.deepEqual(
      api.findAppByRunTitle(applications, titleToSearch),
      applications[0]
    )
  })
})
