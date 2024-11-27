export type VisualMode = '2D' | '3D' | 'Video';

export interface Point {
  x: number;
  y: number;
}

export interface Hold {
  id: string;
  bbox: number[]; // [x_min, y_min, width, height]
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

export interface PlaybackData {
  [key: string]: number;
}

export interface Playback<T extends PlaybackData> {
  hold_id: string;
  frequency: number;
  data: T[] | T;
}

export interface HoldAnnotation extends PlaybackData {
  annotation: number;
}

export interface HoldAnnotationPlayback extends Playback<HoldAnnotation> {}

export interface HoldVector extends PlaybackData {
  x: number;
  y: number;
}

export interface HoldVectorPlayback extends Playback<HoldVector> {}

export type SensorReading = {
  hold_id: string;
  x: number;
  y: number;
};
export type SensorReadingFrame = SensorReading[];

export interface Recording {
  id: string;
  route_id: string;
  start_time: string;
  end_time: string | null;
  sensor_readings: SensorReadingFrame[];
  video_s3_key: string | null;
  status: 'recording' | 'completed' | 'failed';
}

export interface VisualizationData {
  vector_playbacks: HoldVectorPlayback[];
  annotation_playbacks: HoldAnnotationPlayback[];
  plot: PlotData;
}

export interface RecordingAnalysis {
  ai_summary: string;
  key_metrics: KeyMetrics;
  visualizations: {
    load_time_series: VisualizationData;
    load_distribution: VisualizationData;
    load_stability: VisualizationData;
  };
  kinematics?: KinematicsPlayback;
}

export interface AnalysisData {
  summary: {
    ai_summary: string;
    key_metrics: KeyMetrics;
  };
  recordings: RecordingAnalysis[];
  comparison: {
    ai_summary: string;
    visualizations: {
      load_time_series: VisualizationData;
      load_distribution: VisualizationData;
    };
  };
}

export interface KeyMetrics {
  energy_expenditure: number;
  energy_expenditure_rate: number;
  active_duration: number;
  peak_load: number;
  peak_load_rate: number;
  overall_stability: number;
}

export interface PlotData {
  data: Plotly.Data[];
  layout: Partial<Plotly.Layout>;
}

export interface DrawnData {
  bbox: number[]; // [x_min, y_min, width, height]
  mask: boolean[][];
}

export interface PoseLandmark {
  x: number;
  y: number;
  z: number;
  visibility: number;
}

export interface KinematicsFrame {
  timestamp: number;
  landmarks: Record<string, PoseLandmark>;
}

export interface KinematicsPlayback {
  frames: KinematicsFrame[];
  metadata: {
    frame_count: number;
    duration: number;
    fps: number;
    resolution: {
      width: number;
      height: number;
    };
  };
}