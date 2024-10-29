import React, { useContext, useMemo } from 'react';
import { Point } from '../../../types';
import HoldHighlights from './HoldHighlights';
import HoldVectors from './HoldVectors';
import { BoardViewContext } from '../BoardViewContext';
import { HoldAnnotations } from './HoldAnnotations';

interface HoldOverlayProps {
  onMissingHoldClick?: (coords: Point) => void;
  missingHoldMode?: boolean;
}

const HoldOverlay: React.FC<HoldOverlayProps> = ({
  onMissingHoldClick,
  missingHoldMode = false,
}) => {
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
          onHoldClick={handleHoldClick}
          missingHoldMode={missingHoldMode}
        />

        <HoldVectors/>

        <HoldAnnotations/>
      </svg>
    </div>
  );
};

export default HoldOverlay;
