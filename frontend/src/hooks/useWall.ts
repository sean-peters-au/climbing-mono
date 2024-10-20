// src/hooks/useWall.ts
import { useState, useEffect } from 'react';
import API from '../services/api';
import { Wall } from '../types';

const useWall = (id: string | undefined) => {
  const [wall, setWall] = useState<Wall | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWall = async () => {
      try {
        const response = await API.get(`/wall/${id}`);
        setWall(response.data);
      } catch (err) {
        setError('Failed to fetch wall data.');
        console.error('Error fetching wall:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWall();
  }, [id]);

  return { wall, loading, error };
};

export default useWall;