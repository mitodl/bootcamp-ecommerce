// @flow
export type Payment = {
  order: {
    id: number,
    status: string,
    created_on: string,
    updated_on: string,
  },
  klass_key: string,
  price: number,
  description: string,
}

export type Installment = {
  amount: number,
  deadline: string,
}

export type Klass = {
  klass_key: number,
  klass_name: string,
  display_name: string,
  start_date: string,
  end_date: string,
  price: number,
  is_user_eligible_to_pay: boolean,
  total_paid: number,
  payments: Array<Payment>,
  installments: Array<Installment>
}

export type KlassesResponse = Array<Klass>
