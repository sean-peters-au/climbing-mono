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

export interface Climb {
  id: string;
  name: string;
  description: string;
  grade: string;
  date: string;
  hold_ids: string[];
}

export interface Wall {
  id: string;
  name: string;
  height: number;
  width: number;
  image: string; // URL to the wall image
  holds: Hold[];
  routes: Climb[];
}