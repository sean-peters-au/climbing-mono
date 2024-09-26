import React from 'react';
import { Link } from 'react-router-dom';
import useWalls from '../hooks/useWalls';
import { Wall } from '../types';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

const WallList: React.FC = () => {
  const { walls, loading, error } = useWalls();

  if (loading) {
    return <LoadingSpinner message="Loading walls..." />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div>
      <h1>Wall List</h1>
      {walls.length > 0 ? (
        <ul>
          {walls.map((wall: Wall) => (
            <li key={wall.id}>
              <Link to={`/walls/${wall.id}`}>{wall.name}</Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>No walls found. Please create a new wall.</p>
      )}
    </div>
  );
};

export default WallList;