import { configureStore } from '@reduxjs/toolkit';
import formReducer from './slices/formSlice';
import aiReducer from './slices/aiSlice';

export const store = configureStore({
  reducer: {
    form: formReducer,
    ai: aiReducer,
  },
});

