import API from './api';
import { Wall, Route, Recording, AnalysisData } from '../../types';

export type CreateRouteBody = {
  name: string;
  hold_ids: string[];
  grade: string;
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
  },

  deleteHold: async (wallId: string, holdId: string): Promise<void> => {
    await API.delete(`/wall/${wallId}/hold/${holdId}`);
  },

  addHold: async (
    wallId: string,
    holdData: { bbox: number[]; mask: boolean[][] }
  ): Promise<void> => {
    const tempfix = {
      ...holdData,
      mask: holdData.mask.map((row) => row.map((cell) => cell ? 1 : 0)),
    };
    await API.post(`/wall/${wallId}/hold`, tempfix);
  },
};

export const routeQueries = {
  getRoutes: async (wallId: string): Promise<Route[]> => {
    const response = await API.get(`/wall/${wallId}/routes`);
    return response.data.routes;
  },
  
  createRoute: async ({ wallId, routeData }: { wallId: string; routeData: CreateRouteBody }): Promise<Route> => {
    const response = await API.post(`/wall/${wallId}/route`, routeData);
    return response.data;
  },

  updateRoute: async ({
    wallId,
    routeId,
    routeData,
  }: {
    wallId: string;
    routeId: string;
    routeData: CreateRouteBody;
  }): Promise<Route> => {
    const formattedData = {
      ...routeData,
      date: new Date(routeData.date).toISOString()
    };
    
    const response = await API.put(`/wall/${wallId}/route/${routeId}`, formattedData);
    return response.data;
  },
};

export const recordingQueries = {
  getRecordings: async (routeId: string): Promise<Recording[]> => {
    const response = await API.get(`/routes/${routeId}/recordings`);
    return response.data.recordings;
  },
  
  startRecording: async (routeId: string): Promise<Recording> => {
    const response = await API.post('/recording/start', { route_id: routeId });
    return response.data;
  },
  
  stopRecording: async (recordingId: string): Promise<Recording> => {
    const response = await API.post(`/recording/${recordingId}/stop`);
    return response.data;
  },
  
  getAnalysis: async (recordingIds: string[]): Promise<AnalysisData> => {
    const response = await API.post('/recording/analysis', { recording_ids: recordingIds });
    return response.data.analysis_results;
  },

  getRecordingVideoUrl: async (recordingId: string): Promise<string> => {
    const response = await API.get(`/recording/${recordingId}/video`);
    return response.data.video_url;
  },
};