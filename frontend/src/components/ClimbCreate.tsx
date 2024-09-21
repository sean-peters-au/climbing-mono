import React, { useState } from 'react';
import API from '../services/api';

interface Props {
  wallId: string;
  selectedHolds: string[];
}

const ClimbCreate: React.FC<Props> = ({ wallId, selectedHolds }) => {
  const [name, setName] = useState('');
  const [rating, setRating] = useState<number>(0);
  const [sent, setSent] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedHolds.length === 0) {
      alert('Please select at least one hold for the climb.');
      return;
    }

    try {
      await API.post(`/wall/${wallId}/climb`, {
        name,
        rating,
        holds: selectedHolds,
        sent,
      });

      setMessage('Climb created successfully!');
      // Optionally, reset form fields or selected holds
      setName('');
      setRating(0);
      setSent(false);
      // You might also clear selected holds in WallDetail if desired
    } catch (error) {
      console.error('Error creating climb:', error);
      setMessage('Failed to create climb.');
    }
  };

  return (
    <div>
      <h3>Create New Climb</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Climb Name:</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Rating:</label>
          <input
            type="number"
            value={rating}
            onChange={(e) => setRating(Number(e.target.value))}
            required
          />
        </div>
        <div>
          <p>Selected Holds: {selectedHolds.length}</p>
          {selectedHolds.length === 0 && (
            <p style={{ color: 'red' }}>No holds selected.</p>
          )}
        </div>
        <div>
          <label>
            Sent:
            <input
              type="checkbox"
              checked={sent}
              onChange={(e) => setSent(e.target.checked)}
            />
          </label>
        </div>
        <button type="submit">Create Climb</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ClimbCreate;