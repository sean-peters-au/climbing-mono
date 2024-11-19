import React, { useContext, useMemo } from 'react';
import { BoardViewContext } from '../../BoardViewContext';

const HoldVectors: React.FC = () => {
  const { holds, playbackVectors, isPlaying, currentFrame } = useContext(BoardViewContext)!;

  // Memoize drawVectors to prevent unnecessary recalculations
  const drawVectors = useMemo(() => {
    if (!isPlaying || playbackVectors.length === 0) return null;

    return playbackVectors.map((playback, index) => {
      const hold = holds.find((h) => h.id === playback.hold_id);
      if (!hold) return null;

      const [x, y, width, height] = hold.bbox;
      const centerX = x + width / 2;
      const centerY = y + height / 2;

      const scale = 2;
      const vector = Array.isArray(playback.data) ? playback.data[currentFrame] : playback.data;
      const endX = centerX + vector.x * scale;
      const endY = centerY - vector.y * scale;

      return (
        <g key={`sensor-${currentFrame}-${index}`}>
          <line
            x1={centerX}
            y1={centerY}
            x2={endX}
            y2={endY}
            stroke="red"
            strokeWidth={4}
            strokeLinecap="round"
          />
        </g>
      );
    });
  }, [playbackVectors, isPlaying, currentFrame, holds]);

  return <>{drawVectors}</>;
};

export default HoldVectors;