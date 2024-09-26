// src/components/HoldOverlay.tsx
import React, { useEffect, useState } from 'react';
import { Wall, Hold } from '../types';
import { generateHoldImages } from '../utils/holdUtils';

interface HoldOverlayProps {
  wall: Wall;
  holds: Hold[];
  selectedHolds: string[];
  showAllHolds: boolean;
  climbHoldIds: string[];
  onHoldClick: (holdId: string) => void;
}

const HoldOverlay: React.FC<HoldOverlayProps> = ({
  wall,
  holds,
  selectedHolds,
  showAllHolds,
  climbHoldIds,
  onHoldClick,
}) => {
  const [holdImages, setHoldImages] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const images = generateHoldImages(holds);
    setHoldImages(images);
  }, [holds]);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <img
        src={wall.image}
        alt={wall.name}
        style={{ maxWidth: '100%', display: 'block' }}
      />
      <svg
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
        }}
        width="100%"
        height="100%"
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
                cursor: 'pointer',
                pointerEvents: 'all',
              }}
              onClick={(e) => {
                e.stopPropagation();
                onHoldClick(holdId);
              }}
            />
          );
        })}
      </svg>
    </div>
  );
};

export default HoldOverlay;