import API from './api';
import { Wall, Route, Recording, AnalysisData } from '../types';

export type CreateRouteBody = {
  name: string;
  hold_ids: string[];
  grade: number;
  description: string;
  date: string;
};

export const wallQueries = {
  getWalls: async (): Promise<Wall[]> => {
    const response = await API.get('/wall');
    return response.data.walls;
  },
  
  getWall: async (id: string): Promise<Wall> => {
    const response = await API.get(`/wall/${id}`);
    return response.data;
  }
};

export const routeQueries = {
  getRoutes: async (wallId: string): Promise<Route[]> => {
    const response = await API.get(`/wall/${wallId}/routes`);
    return response.data.routes;
  },
  
  createRoute: async ({ wallId, routeData }: { wallId: string; routeData: CreateRouteBody }): Promise<Route> => {
    const response = await API.post(`/wall/${wallId}/route`, routeData);
    return response.data;
  }
};

export const recordingQueries = {
  getRecordings: async (routeId: string): Promise<Recording[]> => {
    const response = await API.get(`/routes/${routeId}/recordings`);
    return response.data.recordings;
  },
  
  createRecording: async (recordingData: Partial<Recording>): Promise<Recording> => {
    const response = await API.post('/recording', recordingData);
    return response.data;
  },
  
  getAnalysis: async (recordingIds: string[]): Promise<AnalysisData> => {
    const response = await API.post('/recording/analysis', { recording_ids: recordingIds });
    return response.data.analysis_results;
  }
};