import _ from 'lodash';
import moment from 'moment';

export const generateFakeKlasses = (numKlasses = 1) => {
  return _.times(numKlasses, (i) => ({
    klass_name: `Klass ${i}`,
    display_title: `Bootcamp Klass ${i}`,
    klass_key: i + 1,
    payment_deadline: moment(),
    total_paid: 0,
    price: 1000,
    is_user_eligible_to_pay: true
  }));
};
