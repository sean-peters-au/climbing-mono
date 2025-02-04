import React, { useContext, useMemo } from 'react';
import { Hold } from '../../../../types';
import { generateHoldImages } from './helpers';
import { BoardViewContext } from '../../BoardViewContext';


const HoldHighlights: React.FC = () => {
  const {
    holds,
    selectedHolds,
    showAllHolds,
    selectedRoute,
    handleHoldClick,
  } = useContext(BoardViewContext)!;

  // Compute climbHoldIds from selectedRoute
  const climbHoldIds = useMemo(() => {
    return selectedRoute ? selectedRoute.holds.map((hold) => hold.id) : [];
  }, [selectedRoute]);

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
              cursor: 'pointer',
              pointerEvents: 'all',
            }}
            onClick={(e) => {
              e.stopPropagation();
              handleHoldClick(holdId);
            }}
          />
        );
      })}
    </>
  );
};

export default HoldHighlights;