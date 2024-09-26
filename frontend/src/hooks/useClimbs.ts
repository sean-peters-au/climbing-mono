// src/hooks/useClimbs.ts
import { useState, useEffect } from 'react';
import API from '../services/api';
import { Climb } from '../types';

export const useClimbs = (wallId: string) => {
  const [climbs, setClimbs] = useState<Climb[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClimbs = async () => {
      try {
        const response = await API.get(`/wall/${wallId}/climbs`);
        setClimbs(response.data.climbs);
      } catch (err) {
        setError('Failed to fetch climbs.');
        console.error('Error fetching climbs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchClimbs();
  }, [wallId]);

  return { climbs, loading, error };
};

export default useClimbs;