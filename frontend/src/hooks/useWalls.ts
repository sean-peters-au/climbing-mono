// src/hooks/useWalls.ts
import { useState, useEffect } from 'react';
import API from '../services/api';
import { Wall } from '../types';

const useWalls = () => {
  const [walls, setWalls] = useState<Wall[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWalls = async () => {
      try {
        const response = await API.get('/wall');
        setWalls(response.data.walls);
      } catch (err) {
        setError('Failed to fetch walls.');
        console.error('Error fetching walls:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWalls();
  }, []);

  return { walls, loading, error };
};

export default useWalls;