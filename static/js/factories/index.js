import _ from "lodash"
import moment from "moment"

export const generateFakeRuns = (
  numRuns = 1,
  { hasInstallment = true, hasPayment = false } = {}
) => {
  return _.times(numRuns, i => {
    const runKey = i + 1
    return {
      bootcamp_run_name:       `Bootcamp Run ${i}`,
      display_title:           `Bootcamp Run ${i}`,
      run_key:                 runKey,
      payment_deadline:        moment(),
      total_paid:              hasPayment ? 100 : 0,
      price:                   1000,
      is_user_eligible_to_pay: true,
      payments:                hasPayment ? [generateFakePayment({ runKey: runKey })] : [],
      installments:            hasInstallment ? [generateFakeInstallment()] : []
    }
  })
}

export const generateFakePayment = ({ runKey = 1, price = 100 } = {}) => ({
  order: {
    id:         runKey + 100,
    status:     "fulfilled",
    created_on: "2017-05-09T13:57:20.414821Z",
    updated_on: "2017-05-09T15:54:54.232055Z"
  },
  run_key:     runKey,
  description: `Installment for Bootcamp Run ${runKey}`,
  price:       price
})

export const generateFakeInstallment = ({
  deadline = undefined,
  amount = 100
} = {}) => ({
  amount:   amount,
  deadline: deadline || moment().format()
})
