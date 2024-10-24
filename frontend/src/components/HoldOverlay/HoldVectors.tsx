import React, { useMemo } from 'react';
import { Hold, SensorReadingFrame } from '../../types';

interface HoldVectorsProps {
  holds: Hold[];
  playbackData?: SensorReadingFrame[];
  currentFrame: number;
  isPlaying: boolean;
}

const HoldVectors: React.FC<HoldVectorsProps> = ({
  holds,
  playbackData,
  currentFrame,
  isPlaying,
}) => {
  // Memoize sensor readings to prevent unnecessary recalculations
  const sensorReadings = useMemo(() => {
    if (!playbackData || !isPlaying) return null;
    const readings = playbackData[currentFrame];
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
  }, [playbackData, isPlaying, currentFrame, holds]);

  return <>{sensorReadings}</>;
};

export default HoldVectors;