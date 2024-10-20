import { useState } from 'react';
import API from '../services/api';
import { Recording } from '../types';

export const useRecordings = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getRecordings = async (routeId: string): Promise<Recording[]> => {
    try {
      setLoading(true);
      const response = await API.get(`/routes/${routeId}/recordings`);
      return response.data;
    } catch (err) {
      setError('Failed to fetch recordings.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { getRecordings, loading, error };
};

export default useRecordings;