import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  interaction_id: null,
  hcp_name: '',
  interaction_type: 'In-person', // Default
  interaction_date: new Date().toISOString().split('T')[0],
  interaction_time: '12:00',
  attendees: [],
  topics_discussed: '',
  materials_shared: [],
  samples_distributed: [],
  sentiment: 'Neutral', // Default
  outcomes: '',
  follow_up_actions: '',
  status: 'Draft',
};

const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    updateField: (state, action) => {
      const { field, value } = action.payload;
      if (field in state) {
        state[field] = value;
      }
    },
    addItem: (state, action) => {
      const { field, item } = action.payload;
      if (Array.isArray(state[field])) {
        state[field].push(item);
      }
    },
    removeItem: (state, action) => {
      const { field, index } = action.payload;
      if (Array.isArray(state[field])) {
        state[field].splice(index, 1);
      }
    },
    populateFromAI: (state, action) => {
      const updates = action.payload; // Array of { field, value }
      updates.forEach(({ field, value }) => {
        if (field in state) {
          state[field] = value;
        }
      });
    },
    resetForm: () => initialState,
  },
});

export const { updateField, addItem, removeItem, populateFromAI, resetForm } = formSlice.actions;
export default formSlice.reducer;
