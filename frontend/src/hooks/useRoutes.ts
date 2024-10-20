// src/hooks/useClimbs.ts
import { useState, useEffect } from 'react';
import API from '../services/api';
import { Route } from '../types';

export const useRoutes = (wallId: string) => {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClimbs = async () => {
      try {
        const response = await API.get(`/wall/${wallId}/routes`);
        setRoutes(response.data.routes);
      } catch (err) {
        setError('Failed to fetch routes.');
        console.error('Error fetching routes:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchClimbs();
  }, [wallId]);

  return { routes, loading, error };
};

export default useRoutes;