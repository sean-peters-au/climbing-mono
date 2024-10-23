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

export type CreateRouteData = {
  name: string;
  grade: number;
  description: string;
  hold_ids: string[];
  date: string;
};

export const useCreateRoute = (wallId: string) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const createRoute = async (routeData: CreateRouteData): Promise<Route> => {
    try {
      setLoading(true);
      const response = await API.post(`/wall/${wallId}/route`, routeData);
      return response.data;
    } catch (err) {
      setError('Failed to create route.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createRoute, loading, error };
};