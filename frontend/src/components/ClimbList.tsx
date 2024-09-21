import React from 'react';
import { Climb } from '../types';

interface Props {
  climbs: Climb[];
}

const ClimbList: React.FC<Props> = ({ climbs }) => (
  <ul>
    {climbs.map((climb) => (
      <li key={climb.id}>
        <strong>{climb.name}</strong> - Rating: {climb.rating} -{' '}
        {climb.sent ? 'Sent' : 'Not Sent'}
      </li>
    ))}
  </ul>
);

export default ClimbList;