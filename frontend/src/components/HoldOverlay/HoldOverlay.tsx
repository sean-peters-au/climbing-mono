import React, { useState, useEffect, useRef } from 'react';
import { Wall, Hold, Point, SensorReadingFrame } from '../../types';
import HoldHighlights from './HoldHighlights';
import HoldVectors from './HoldVectors';

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
  }, [isPlaying, playbackData]);

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (missingHoldMode && onMissingHoldClick) {
      const rect = event.currentTarget.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * wall.width;
      const y = ((event.clientY - rect.top) / rect.height) * wall.height;
      onMissingHoldClick({ x, y });
    }
  };

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
        {/* Render Hold Highlights */}
        <HoldHighlights
          holds={holds}
          selectedHolds={selectedHolds}
          showAllHolds={showAllHolds}
          climbHoldIds={climbHoldIds}
          onHoldClick={onHoldClick}
          missingHoldMode={missingHoldMode}
        />

        {/* Render Hold Vectors */}
        <HoldVectors
          holds={holds}
          playbackData={playbackData}
          currentFrame={currentFrame}
          isPlaying={isPlaying}
        />

        {/* Additional overlays can be added here */}
      </svg>
    </div>
  );
};

export default HoldOverlay;