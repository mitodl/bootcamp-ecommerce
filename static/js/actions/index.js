export const UPDATE_CHECKBOX = 'UPDATE_CHECKBOX';

export const updateCheckbox = checked => ({
  type: UPDATE_CHECKBOX,
  payload: { checked }
});
