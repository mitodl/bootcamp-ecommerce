// @flow
export type Payment = {
  order: {
    id: number,
    status: string,
    created_on: string,
    updated_on: string,
  },
  run_key: number,
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
  bootcamp_location: string,
  bootcamp_location_details: string,
}

export type BootcampRun = {
  id: number,
  display_title: string,
  title: string,
  run_key: string,
  start_date: ?string,
  end_date: ?string,
  novoed_course_stub: ?string,
  bootcamp: Bootcamp,
  page?: ?BootcampRunPage,
  installments: Array<Installment>,
  is_payable: boolean,
  allows_skipped_steps: boolean,
}

export type BootcampRunEnrollment = {
  id: number,
  user_id: number,
  bootcamp_run_id: number,
  novoed_sync_date: ?string,
}

export type PayableBootcampRun = {
  run_key: number,
  bootcamp_run_name: string,
  display_title: string,
  start_date: string,
  end_date: string,
  price: number,
  total_paid: number,
  payments: Array<Payment>,
  installments: Array<Installment>
}

export type PayableRunsResponse = Array<PayableBootcampRun>
