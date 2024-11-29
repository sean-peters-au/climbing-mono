import React, { useContext, useMemo } from 'react';
import HoldHighlights from './HoldHighlights';
import HoldVectors from './HoldVectors';
import { BoardViewContext } from '../../BoardViewContext';
import { HoldAnnotations } from './HoldAnnotations';

const HoldOverlay: React.FC = () => {
  const {
    wall,
    holds,
    selectedHolds,
    showAllHolds,
    handleHoldClick,
    selectedRoute,
  } = useContext(BoardViewContext)!;

  // Compute climbHoldIds from selectedRoute
  const climbHoldIds = useMemo(() => {
    return selectedRoute ? selectedRoute.holds.map((hold) => hold.id) : [];
  }, [selectedRoute]);

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        cursor: 'crosshair',
        pointerEvents: 'none',
      }}
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
          onHoldClick={handleHoldClick}
        />

        <HoldVectors/>

        <HoldAnnotations/>
      </svg>
    </div>
  );
};

export default HoldOverlay;
