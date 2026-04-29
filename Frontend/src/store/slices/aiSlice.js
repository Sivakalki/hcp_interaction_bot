import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { chatWithAI } from '../../api/aiApi';
import { populateFromAI } from './formSlice';

export const sendMessage = createAsyncThunk(
  'ai/sendMessage',
  async ({ content, sessionId }, { getState, dispatch, rejectWithValue }) => {
    try {
      const state = getState();
      const interaction_id = state.form.interaction_id;
      const formData = state.form;
      
      const currentMessage = { role: 'user', content };
      
      const response = await chatWithAI({ 
        messages: [currentMessage], 
        session_id: sessionId,
        interaction_id: interaction_id,
        form_data: formData
      });
      
      // If the AI returned form updates, dispatch them to the form slice
      if (response.form_updates && response.form_updates.length > 0) {
        dispatch(populateFromAI(response.form_updates));
      }
      
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const aiSlice = createSlice({
  name: 'ai',
  initialState: {
    messages: [],
    sessionId: null,
    status: 'idle',
    error: null,
    isOpen: false,
  },
  reducers: {
    toggleSidebar: (state) => {
      state.isOpen = !state.isOpen;
    },
    clearChat: (state) => {
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state, action) => {
        state.status = 'loading';
        state.messages.push({ role: 'user', content: action.meta.arg.content });
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.messages.push({ role: 'assistant', content: action.payload.reply });
        state.sessionId = action.payload.session_id;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
        state.messages.push({ 
          role: 'assistant', 
          content: `⚠️ Bot Error: ${action.payload || 'Failed to connect to AI service. Please check your connection or API keys.'}`,
          isError: true 
        });
      });
  },
});

export const { toggleSidebar, clearChat } = aiSlice.actions;
export default aiSlice.reducer;
