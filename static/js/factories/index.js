import _ from "lodash"
import moment from "moment"

export const generateFakeKlasses = (
  numKlasses = 1,
  { hasInstallment = true, hasPayment = false } = {}
) => {
  return _.times(numKlasses, i => {
    const klassKey = i + 1
    return {
      klass_name:              `Klass ${i}`,
      display_title:           `Bootcamp Klass ${i}`,
      klass_key:               klassKey,
      payment_deadline:        moment(),
      total_paid:              hasPayment ? 100 : 0,
      price:                   1000,
      is_user_eligible_to_pay: true,
      payments:                hasPayment ? [generateFakePayment({ klassKey: klassKey })] : [],
      installments:            hasInstallment ? [generateFakeInstallment()] : []
    }
  })
}

export const generateFakePayment = ({ klassKey = 1, price = 100 } = {}) => ({
  order: {
    id:         klassKey + 100,
    status:     "fulfilled",
    created_on: "2017-05-09T13:57:20.414821Z",
    updated_on: "2017-05-09T15:54:54.232055Z"
  },
  klass_key:   klassKey,
  description: `Installment for Klass ${klassKey}`,
  price:       price
})

export const generateFakeInstallment = ({
  deadline = undefined,
  amount = 100
} = {}) => ({
  amount:   amount,
  deadline: deadline || moment().format()
})
