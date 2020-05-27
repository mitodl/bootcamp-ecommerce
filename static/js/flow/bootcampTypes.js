// @flow
export type Payment = {
  order: {
    id: number,
    status: string,
    created_on: string,
    updated_on: string,
  },
  run_key: string,
  price: number,
  description: string,
}

export type Installment = {
  amount: number,
  deadline: string,
}

export type BootcampRun = {
  run_key: number,
  bootcamp_run_name: string,
  display_name: string,
  start_date: string,
  end_date: string,
  price: number,
  total_paid: number,
  payments: Array<Payment>,
  installments: Array<Installment>
}

export type BootcampRunsResponse = Array<BootcampRun>
