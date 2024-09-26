// src/components/WallDetail.tsx
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import useWall from '../hooks/useWall';
import useClimbs from '../hooks/useClimbs';
import { Hold } from '../types';
import ClimbList from './ClimbList';
import ClimbCreate from './ClimbCreate';
import HoldOverlay from './HoldOverlay';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

const WallDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { wall, loading: wallLoading, error: wallError } = useWall(id!);
  const { climbs, loading: climbsLoading, error: climbsError } = useClimbs(id!);
  const [selectedHolds, setSelectedHolds] = useState<string[]>([]);
  const [showAllHolds, setShowAllHolds] = useState<boolean>(false);
  const [selectedClimbId, setSelectedClimbId] = useState<string | null>(null);

  if (wallLoading || climbsLoading) {
    return <LoadingSpinner message="Loading wall details..." />;
  }

  if (wallError || !wall) {
    return <ErrorMessage message={wallError || 'Wall not found.'} />;
  }

  const handleHoldClick = (holdId: string) => {
    setSelectedHolds((prevSelected) =>
      prevSelected.includes(holdId)
        ? prevSelected.filter((id) => id !== holdId)
        : [...prevSelected, holdId]
    );
  };

  const selectedClimb = climbs.find((climb) => climb.id === selectedClimbId);

  return (
    <div>
      <h1>{wall.name}</h1>
      <button onClick={() => setShowAllHolds(!showAllHolds)}>
        {showAllHolds ? 'Hide All Holds' : 'Show All Holds'}
      </button>
      <HoldOverlay
        wall={wall}
        holds={wall.holds}
        selectedHolds={selectedHolds}
        showAllHolds={showAllHolds}
        climbHoldIds={selectedClimb?.hold_ids || []}
        onHoldClick={handleHoldClick}
      />
      <h2>Climbs</h2>
      {climbsError ? (
        <ErrorMessage message={climbsError} />
      ) : (
        <ClimbList
          climbs={climbs}
          selectedClimbId={selectedClimbId}
          onSelectClimb={setSelectedClimbId}
        />
      )}
      <ClimbCreate wallId={wall.id} selectedHolds={selectedHolds} />
      <button onClick={() => setSelectedHolds([])}>Reset Hold Selection</button>
    </div>
  );
};

export default WallDetail;