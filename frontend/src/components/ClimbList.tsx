// src/components/ClimbList.tsx
import React from 'react';
import { Climb } from '../types';
import './ClimbList.css';

interface ClimbListProps {
  climbs: Climb[];
  selectedClimbId: string | null;
  onSelectClimb: (climbId: string | null) => void;
}

const ClimbList: React.FC<ClimbListProps> = ({ climbs, selectedClimbId, onSelectClimb }) => {
  if (!climbs || climbs.length === 0) {
    return <div>No climbs available for this wall.</div>;
  }

  const handleClimbClick = (climbId: string) => {
    if (selectedClimbId === climbId) {
      onSelectClimb(null); // Deselect if already selected
    } else {
      onSelectClimb(climbId);
    }
  };

  return (
    <table className="climb-list">
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Grade</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {climbs.map((climb) => (
          <tr
            key={climb.id}
            className={climb.id === selectedClimbId ? 'selected' : ''}
            onClick={() => handleClimbClick(climb.id)}
            style={{ cursor: 'pointer' }}
          >
            <td>{climb.name}</td>
            <td>{climb.description}</td>
            <td>{climb.grade}</td>
            <td>{climb.date?.substring(0, 10)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ClimbList;