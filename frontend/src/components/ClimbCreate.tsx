// src/components/ClimbCreate.tsx
import React, { useState } from 'react';
import API from '../services/api';
import './ClimbCreate.css';

interface Props {
  wallId: string;
  selectedHolds: string[];
}

const ClimbCreate: React.FC<Props> = ({ wallId, selectedHolds }) => {
  const [formData, setFormData] = useState({
    name: '',
    grade: '',
    description: '',
  });
  const [message, setMessage] = useState<string>('');

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const target = e.target as HTMLInputElement;
    const { name, value, type, checked } = target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedHolds.length === 0) {
      alert('Please select at least one hold for the climb.');
      return;
    }

    try {
      await API.post(`/wall/${wallId}/climb`, {
        ...formData,
        hold_ids: selectedHolds,
        date: new Date().toISOString(),
      });

      setMessage('Climb created successfully!');
      setFormData({
        name: '',
        grade: '',
        description: '',
      });
    } catch (error) {
      console.error('Error creating climb:', error);
      setMessage('Failed to create climb.');
    }
  };

  return (
    <div className="climb-create">
      <h3>Create New Climb</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Climb Name:</label>
          <input
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Grade:</label>
          <input
            name="grade"
            value={formData.grade}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Description:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
          />
        </div>
        <div>
          <p>Selected Holds: {selectedHolds.length}</p>
          {selectedHolds.length === 0 && (
            <p style={{ color: 'red' }}>No holds selected.</p>
          )}
        </div>
        <button type="submit">Create Climb</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ClimbCreate;