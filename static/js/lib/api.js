// @flow
import { fetchJSONWithCSRF } from './api_util';

export type PaymentResponse = {};
export function sendPayment(total: string): Promise<PaymentResponse> {
  return fetchJSONWithCSRF(`/api/v0/payment/`, {
    method: 'POST',
    body: JSON.stringify({
      total: total,
    })
  });
}
