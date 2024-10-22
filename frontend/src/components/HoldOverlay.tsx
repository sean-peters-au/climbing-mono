import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Wall, Hold, Point, SensorReadingFrame } from '../types';
import { generateHoldImages } from '../utils/holdUtils';

interface HoldOverlayProps {
  wall: Wall;
  holds: Hold[];
  selectedHolds: string[];
  showAllHolds: boolean;
  climbHoldIds: string[];
  onHoldClick: (holdId: string) => void;
  onMissingHoldClick?: (coords: Point) => void;
  missingHoldMode?: boolean;
  playbackData?: SensorReadingFrame[];
}

const HoldOverlay: React.FC<HoldOverlayProps> = ({
  wall,
  holds,
  selectedHolds,
  showAllHolds,
  climbHoldIds,
  onHoldClick,
  onMissingHoldClick,
  missingHoldMode = false,
  playbackData,
}) => {
  const [currentFrame, setCurrentFrame] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const playbackIntervalRef = useRef<number | null>(null);

  // Constants for frame rate control
  const FRAME_RATE = 100; // Desired frame rate in Hz
  const FRAME_DURATION_MS = 1000 / FRAME_RATE; // Duration of each frame in ms

  // Start playback when playbackData changes
  useEffect(() => {
    if (playbackData && playbackData.length > 0) {
      setIsPlaying(true);
      setCurrentFrame(0);
    } else {
      setIsPlaying(false);
      setCurrentFrame(0);
    }
  }, [playbackData]);

  // Playback mechanism using setInterval
  useEffect(() => {
    if (isPlaying && playbackData) {
      const totalFrames = playbackData.length;

      playbackIntervalRef.current = window.setInterval(() => {
        setCurrentFrame((prevFrame) => {
          const nextFrame = prevFrame + 1;
          if (nextFrame >= totalFrames) {
            // Stop playback when all frames have been played
            if (playbackIntervalRef.current !== null) {
              clearInterval(playbackIntervalRef.current);
              playbackIntervalRef.current = null;
            }
            setIsPlaying(false);
            return prevFrame;
          } else {
            return nextFrame;
          }
        });
      }, FRAME_DURATION_MS);

      // Cleanup function to clear the interval when the component unmounts or playback stops
      return () => {
        if (playbackIntervalRef.current !== null) {
          clearInterval(playbackIntervalRef.current);
          playbackIntervalRef.current = null;
        }
      };
    }
  }, [FRAME_DURATION_MS, isPlaying, playbackData]);

  // Generate hold images
  const holdImages = useMemo(() => generateHoldImages(holds), [holds]);

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (missingHoldMode && onMissingHoldClick) {
      const rect = event.currentTarget.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * wall.width;
      const y = ((event.clientY - rect.top) / rect.height) * wall.height;
      onMissingHoldClick({ x, y });
    }
  };

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

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        cursor: missingHoldMode ? 'crosshair' : 'default',
      }}
      onClick={handleOverlayClick}
    >
      <svg
        style={{
          width: '100%',
          height: '100%',
        }}
        viewBox={`0 0 ${wall.width} ${wall.height}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Render holds */}
        {holds.map((hold: Hold) => {
          const holdId = hold.id;
          const isSelected = selectedHolds.includes(holdId);
          const isClimbHold = climbHoldIds.includes(holdId);
          const isVisible = showAllHolds || isSelected || isClimbHold;
          const [x, y, width, height] = hold.bbox;

          return (
            <image
              key={holdId}
              href={holdImages[holdId]}
              x={x}
              y={y}
              width={width}
              height={height}
              style={{
                opacity: isVisible ? (isSelected || isClimbHold ? 0.8 : 0.5) : 0,
                cursor: missingHoldMode ? 'not-allowed' : 'pointer',
                pointerEvents: missingHoldMode ? 'none' : 'all',
              }}
              onClick={(e) => {
                e.stopPropagation();
                if (!missingHoldMode) {
                  onHoldClick(holdId);
                }
              }}
            />
          );
        })}

        {/* Render sensor readings */}
        {sensorReadings}
      </svg>
    </div>
  );
};

export default HoldOverlay;
