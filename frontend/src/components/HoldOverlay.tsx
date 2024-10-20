import React, { useEffect, useState } from 'react';
import { Wall, Hold, Point } from '../types';
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
}) => {
  const [holdImages, setHoldImages] = useState<{ [key: string]: string }>({});

  console.log('selected holds', selectedHolds);
  useEffect(() => {
    console.log('selected holds', selectedHolds);
  }, [selectedHolds]);

  useEffect(() => {
    const images = generateHoldImages(holds);
    setHoldImages(images);
  }, [holds]);

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
      </svg>
    </div>
  );
};

export default HoldOverlay;