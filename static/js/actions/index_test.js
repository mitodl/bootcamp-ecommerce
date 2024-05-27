import { assertCreatedActionHelper } from "./test_util";

import {
  setSelectedBootcampRunKey,
  setPaymentAmount,
  setInitialTime,
  setTimeoutActive,
  setToastMessage,
  SET_SELECTED_BOOTCAMP_RUN_KEY,
  SET_PAYMENT_AMOUNT,
  SET_INITIAL_TIME,
  SET_TIMEOUT_ACTIVE,
  SET_TOAST_MESSAGE,
} from "./index";

describe("actions", () => {
  it("should create all action creators", () => {
    [
      [setPaymentAmount, SET_PAYMENT_AMOUNT],
      [setSelectedBootcampRunKey, SET_SELECTED_BOOTCAMP_RUN_KEY],
      [setInitialTime, SET_INITIAL_TIME],
      [setTimeoutActive, SET_TIMEOUT_ACTIVE],
      [setToastMessage, SET_TOAST_MESSAGE],
    ].forEach(assertCreatedActionHelper);
  });
});
