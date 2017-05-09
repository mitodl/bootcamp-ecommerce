import _ from 'lodash';
import moment from 'moment';

export const generateFakeKlasses = (numKlasses = 1, hasPayment = false) => {
  return _.times(numKlasses, (i) => {
    let payments = [];
    if (hasPayment) {
      payments = [{
        "order": {
          "id": i + 100,
          "status": 'fulfilled',
          "created_on": "2017-05-09T13:57:20.414821Z",
          "updated_on": "2017-05-09T15:54:54.232055Z"
        },
        "klass_key": i + 1,
        "description": "Installment for Class 2 (Student)",
      }];
    }

    return {
      klass_name: `Klass ${i}`,
      display_title: `Bootcamp Klass ${i}`,
      klass_key: i + 1,
      payment_deadline: moment(),
      total_paid: hasPayment ? 200 : 0,
      price: 1000,
      is_user_eligible_to_pay: true,
      payments: payments
    };
  });
};
