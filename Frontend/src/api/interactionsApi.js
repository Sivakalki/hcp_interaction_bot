const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const createInteraction = async (data) => {
  const response = await fetch(`${API_BASE_URL}/interactions/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create interaction');
  }

  return response.json();
};

export const listInteractions = async () => {
  const response = await fetch(`${API_BASE_URL}/interactions/`);
  if (!response.ok) throw new Error('Failed to fetch interactions');
  return response.json();
};

export const getInteractionDetail = async (id) => {
  const response = await fetch(`${API_BASE_URL}/interactions/${id}`);
  if (!response.ok) throw new Error('Failed to fetch interaction details');
  return response.json();
};

export const updateInteraction = async (id, data) => {
  const response = await fetch(`${API_BASE_URL}/interactions/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to update interaction');
  }

  return response.json();
};
