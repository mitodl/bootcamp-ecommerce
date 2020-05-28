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

export type Bootcamp = {
  id: number,
  title: string,
}

export type BootcampRunPage = {
  description: ?string,
  subhead: string,
  thumbnail_image_src: ?string,
}

export type BootcampRun = {
  id: number,
  display_title: string,
  title: string,
  run_key: string,
  start_date: ?string,
  end_date: ?string,
  bootcamp: Bootcamp,
  page?: ?BootcampRunPage,
}

export type PayableBootcampRun = {
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

export type BootcampRunsResponse = Array<PayableBootcampRun>
