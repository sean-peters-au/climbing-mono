export interface Hold {
  id: string;
  bbox: number[]; // [x1, y1, x2, y2]
  centroid_x: number;
  centroid_y: number;
  mask: number[][]; // 2D array representing the hold mask
}

export interface Climb {
  id: string;
  name: string;
  rating: number;
  holds: Hold[]; // Holds that make up the climb
  sent: boolean;
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