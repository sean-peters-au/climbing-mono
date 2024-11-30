import React, { useMemo } from 'react';
import { Hold } from '../../../../types';
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
        const borderThickness = 5; // Must match the borderThickness in helpers.ts

        return (
          <image
            key={holdId}
            href={holdImages[holdId]}
            x={x - borderThickness} // Offset x to center the border
            y={y - borderThickness} // Offset y to center the border
            width={width + borderThickness * 2} // Increase width to accommodate border
            height={height + borderThickness * 2} // Increase height to accommodate border
            style={{
              opacity: isVisible ? 0.8 : 0, // Set consistent opacity
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