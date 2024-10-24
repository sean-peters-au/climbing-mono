import React, { useMemo } from 'react';
import { Hold } from '../../types';
import { generateHoldImages } from './helpers';

interface HoldHighlightsProps {
  holds: Hold[];
  selectedHolds: string[];
  showAllHolds: boolean;
  climbHoldIds: string[];
  onHoldClick: (holdId: string) => void;
  missingHoldMode?: boolean;
}

const HoldHighlights: React.FC<HoldHighlightsProps> = ({
  holds,
  selectedHolds,
  showAllHolds,
  climbHoldIds,
  onHoldClick,
  missingHoldMode = false,
}) => {
  // Generate hold images
  const holdImages = useMemo(() => generateHoldImages(holds), [holds]);

  return (
    <>
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
    </>
  );
};

export default HoldHighlights;