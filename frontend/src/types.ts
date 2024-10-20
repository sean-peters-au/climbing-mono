// src/types.ts
export interface Point {
  x: number;
  y: number;
}

export interface Hold {
  id: string;
  bbox: number[]; // [x, y, width, height]
  centroid_x: number;
  centroid_y: number;
  mask: boolean[][]; // 2D array representing the hold mask
}

export interface Route {
  id: string;
  name: string;
  description: string;
  grade: string;
  date: string;
  holds: Hold[];
}

export interface Wall {
  id: string;
  name: string;
  height: number;
  width: number;
  image_url: string;
  holds: Hold[];
  routes: Route[];
}

export type SensorReading = {
  hold_id: string;
  x: number;
  y: number;
};

export type Recording = {
  id: string;
  route_id: string;
  start_time: string;
  end_time: string;
  sensor_readings: SensorReading[];
};
