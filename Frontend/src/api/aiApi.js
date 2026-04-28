const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const chatWithAI = async (data) => {
  const response = await fetch(`${API_BASE_URL}/ai/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to communicate with AI');
  }

  return response.json();
};
