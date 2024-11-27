import React, { useEffect, useContext } from 'react';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Button,
} from '@mui/material';
import Plot from 'react-plotly.js';
import { BoardViewContext } from '../../BoardViewContext';
import { useRecordingsAnalysis } from '../../../../hooks/useRecordings';
import { QueryError } from '../../../QueryError';
import { interpolatePlayback } from '../../VisualPanel/HoldOverlay/helpers';
import { KeyMetrics } from './KeyMetrics';
import { HoldAnnotationPlayback, HoldVectorPlayback } from '../../../../types';

interface SingleAnalysisProps {
  selectedRecordingIds: string[];
}

export const SingleAnalysis: React.FC<SingleAnalysisProps> = ({
  selectedRecordingIds,
}) => {
  const {
    isPlaying,
    setIsPlaying,
    frameRate,
    setPlaybackVectors,
    setPlaybackAnnotations,
    setPlaybackFrames,
    setPlaybackKinematics,
    setCurrentFrame,
    currentFrame,
  } = useContext(BoardViewContext)!;

  const { data: analysisData, isLoading, error } = useRecordingsAnalysis(selectedRecordingIds);

  // State to manage which visualization is being played
  const [activeVisualization, setActiveVisualization] = React.useState<'load_time_series' | 'load_distribution' | 'load_stability' | null>(null);

  useEffect(() => {
    if (analysisData) {
      // For load_time_series visualization
      const vectorPlaybacksTimeSeries = analysisData.recordings[0].visualizations.load_time_series.vector_playbacks.map(
        playback => interpolatePlayback(playback)
      );
      const annotationPlaybacksTimeSeries = analysisData.recordings[0].visualizations.load_time_series.annotation_playbacks.map(playback => interpolatePlayback(playback));

      // For load_distribution visualization
      const vectorPlaybacksDistribution = analysisData.recordings[0].visualizations.load_distribution.vector_playbacks.map(
        playback => interpolatePlayback(playback)
      );
      const annotationPlaybacksDistribution = analysisData.recordings[0].visualizations.load_distribution.annotation_playbacks.map(playback => interpolatePlayback(playback));

      // For load_stability visualization
      const vectorPlaybacksStability = analysisData.recordings[0].visualizations.load_stability.vector_playbacks.map(
        playback => interpolatePlayback(playback)
      );
      const annotationPlaybacksStability = analysisData.recordings[0].visualizations.load_stability.annotation_playbacks.map(playback => interpolatePlayback(playback));

      // Choose which playback data to use based on activeVisualization
      let vectorPlaybacks: HoldVectorPlayback[];
      let annotationPlaybacks: HoldAnnotationPlayback[];

      if (activeVisualization === 'load_time_series') {
        vectorPlaybacks = vectorPlaybacksTimeSeries;
        annotationPlaybacks = annotationPlaybacksTimeSeries;
      } else if (activeVisualization === 'load_distribution') {
        vectorPlaybacks = vectorPlaybacksDistribution;
        annotationPlaybacks = annotationPlaybacksDistribution;
      } else if (activeVisualization === 'load_stability') {
        vectorPlaybacks = vectorPlaybacksStability;
        annotationPlaybacks = annotationPlaybacksStability;
      } else {
        vectorPlaybacks = [];
        annotationPlaybacks = [];
      }

      if (vectorPlaybacks.length > 0) {
        setPlaybackVectors(vectorPlaybacks);
        setPlaybackAnnotations(annotationPlaybacks);
        setPlaybackFrames(vectorPlaybacks[0].data.length);
      }

      // Set kinematics playback data
      if (analysisData.recordings[0]?.kinematics ) {
        setPlaybackKinematics(analysisData.recordings[0].kinematics);
      } else {
        setPlaybackKinematics(null);
      }
    }
  }, [
    analysisData,
    activeVisualization,
    frameRate,
    setPlaybackAnnotations,
    setPlaybackVectors,
    setPlaybackFrames,
    setPlaybackKinematics
  ]);

  const handlePlay = (visualizationType: 'load_time_series' | 'load_distribution' | 'load_stability') => {
    setActiveVisualization(visualizationType);
    setIsPlaying(true);
    setCurrentFrame(0);
  };

  const updatePlotLayout = (originalLayout: Partial<Plotly.Layout>) => ({
    ...originalLayout,
    shapes: [
      ...(originalLayout.shapes || []),
      {
        type: 'line' as const,
        x0: currentFrame / 100,
        x1: currentFrame / 100,
        y0: 0,
        y1: 1,
        yref: 'paper' as const,
        line: {
          color: 'white',
          width: 4,
        },
      },
    ],
  });

  if (error) {
    return <QueryError error={error} />;
  }

  if (isLoading) {
    return (
      <Box sx={{ mt: 2 }}>
        <CircularProgress />
        <Typography>Loading analysis...</Typography>
      </Box>
    );
  }

  if (!analysisData) {
    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="body1">Select recordings to view analysis.</Typography>
      </Box>
    );
  }

  const recording = analysisData.recordings[0]; // For individual analysis

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Analysis for Recording {selectedRecordingIds[0]}
      </Typography>

      <KeyMetrics recordingAnalysis={recording} />

      {/* Load Time Series Visualization */}
      <Box sx={{ mt: 4 }}>
        <Box sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingBottom: 1,
        }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontSize: '1.6rem', paddingLeft: 1 }}>
            Load on Each Hold Over Time
          </Typography>
          <Button variant="contained" onClick={() => handlePlay('load_time_series')}>
            {(isPlaying && activeVisualization === 'load_time_series') ? 'Playing...' : 'Play'}
          </Button>
        </Box>
        <Plot
          data={recording.visualizations.load_time_series.plot.data}
          layout={updatePlotLayout(recording.visualizations.load_time_series.plot.layout)}
          useResizeHandler
          style={{ width: '100%', height: '400px' }}
          config={{ responsive: true }}
        />
      </Box>

      {/* Load Distribution Visualization */}
      <Box sx={{ mt: 4 }}>
        <Box sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingBottom: 1,
        }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontSize: '1.6rem', paddingLeft: 1 }}>
            Load Distribution Over Time
          </Typography>
          <Button variant="contained" onClick={() => handlePlay('load_distribution')}>
            {(isPlaying && activeVisualization === 'load_distribution') ? 'Playing...' : 'Play'}
          </Button>
        </Box>
        <Plot
          data={recording.visualizations.load_distribution.plot.data}
          layout={updatePlotLayout(recording.visualizations.load_distribution.plot.layout)}
          useResizeHandler
          style={{ width: '100%', height: '400px' }}
          config={{ responsive: true }}
        />
      </Box>

      {/* Load Stability Visualization */}
      <Box sx={{ mt: 4 }}>
        <Box sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingBottom: 1,
        }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontSize: '1.6rem', paddingLeft: 1 }}>
            Load Stability Over Time
          </Typography>
          <Button variant="contained" onClick={() => handlePlay('load_stability')}>
            {(isPlaying && activeVisualization === 'load_stability') ? 'Playing...' : 'Play'}
          </Button>
        </Box>
        <Plot
          data={recording.visualizations.load_stability.plot.data}
          layout={updatePlotLayout(recording.visualizations.load_stability.plot.layout)}
          useResizeHandler
          style={{ width: '100%', height: '400px' }}
          config={{ responsive: true }}
        />
      </Box>
    </Box>
  );
};
