import React, { useState, useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { SensorReadingFrame, Hold } from '../types';

interface SVGVisualizationProps {
  sensorReadings: SensorReadingFrame[]; // Time-series data
  holds: Hold[];
}

const SVGVisualization: React.FC<SVGVisualizationProps> = ({ sensorReadings, holds }) => {
  const [currentFrame, setCurrentFrame] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const playbackIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (sensorReadings && sensorReadings.length > 0) {
      setIsPlaying(true);
      setCurrentFrame(0);
    } else {
      setIsPlaying(false);
      setCurrentFrame(0);
    }
  }, [sensorReadings]);

  useEffect(() => {
    if (isPlaying) {
      const totalFrames = sensorReadings.length;
      const playbackSpeed = 10; // 100 Hz => 10ms per frame

      playbackIntervalRef.current = window.setInterval(() => {
        setCurrentFrame((prevFrame) => {
          if (prevFrame + 1 >= totalFrames) {
            // Stop playback
            if (playbackIntervalRef.current !== null) {
              clearInterval(playbackIntervalRef.current);
            }
            setIsPlaying(false);
            return prevFrame;
          } else {
            return prevFrame + 1;
          }
        });
      }, playbackSpeed);

      return () => {
        if (playbackIntervalRef.current !== null) {
          clearInterval(playbackIntervalRef.current);
        }
      };
    }
  }, [isPlaying, sensorReadings]);

  const renderSensorReadings = () => {
    if (!sensorReadings || !isPlaying) return null;

    const readings = sensorReadings[currentFrame];
    if (!readings) return null;

    return readings.map((reading, index) => {
      const hold = holds.find((h) => h.id === reading.hold_id);
      if (!hold) return null;

      const [x, y, width, height] = hold.bbox;
      const centerX = x + width / 2;
      const centerY = y + height / 2;

      const scale = 1.0; // Adjust scaling factor as needed
      const endX = centerX + reading.x * scale;
      const endY = centerY - reading.y * scale;

      return (
        <g key={`sensor-${currentFrame}-${index}`}>
          <line
            x1={centerX}
            y1={centerY}
            x2={endX}
            y2={endY}
            stroke="red"
            strokeWidth={4} // Thicker lines
            strokeLinecap="round"
          />
        </g>
      );
    });
  };

  return (
    <Box mt={2}>
      <svg width="100%" height="100%" viewBox={`0 0 800 600`}>
        {/* Draw Holds */}
        {holds.map((hold) => {
          const [x, y, width, height] = hold.bbox;
          return (
            <rect
              key={hold.id}
              x={x}
              y={y}
              width={width}
              height={height}
              fill="blue"
              opacity={0.3}
            />
          );
        })}

        {/* Render Sensor Readings */}
        {renderSensorReadings()}
      </svg>
    </Box>
  );
};

export default SVGVisualization;