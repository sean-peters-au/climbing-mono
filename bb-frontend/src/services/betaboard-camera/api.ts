import axios from 'axios';

const CAMERA_API_URL = process.env.REACT_APP_BB_CAMERA_URL;
export const CAMERA_STREAM_URL = `${CAMERA_API_URL}/video_feed`; 

const cameraAPI = axios.create({
  baseURL: CAMERA_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  responseType: 'blob',
});

export const getCameraPhoto = async (): Promise<Blob> => {
  const response = await cameraAPI.get('/capture_photo');
  return response.data;
}; 