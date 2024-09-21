import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import API from '../services/api';
import { Wall } from '../types';

const WallList: React.FC = () => {
  const [walls, setWalls] = useState<Wall[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWalls = async () => {
      try {
        const response = await API.get('/wall');
        setWalls(response.data.walls);
      } catch (err) {
        setError('Failed to fetch walls');
        console.error('Error fetching walls:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWalls();
  }, []);

  if (loading) {
    return <div>Loading walls...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h1>Wall List</h1>
      <Link to="/walls/new">Create New Wall</Link>
      {walls.length > 0 ? (
        <ul>
          {walls.map((wall) => (
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