import React from 'react';
import { Climb } from '../types';

interface ClimbListProps {
  climbs: Climb[];
}

const ClimbList: React.FC<ClimbListProps> = ({ climbs }) => {
  if (!climbs || climbs.length === 0) {
    return <div>No climbs available for this wall.</div>;
  }

  return (
    <ul>
      {climbs.map((climb) => (
        <li key={climb.id}>
          <h3>{climb.name}</h3>
          <p>Description: {climb.description}</p>
          <p>Grade: {climb.grade}</p>
          <p>Date: {climb.date}</p>
        </li>
      ))}
    </ul>
  );
};

export default ClimbList;