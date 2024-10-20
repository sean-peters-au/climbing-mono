// src/components/WallCreate.tsx
import React, { useState } from 'react';
import API from '../services/api';
import { useNavigate } from 'react-router-dom';
import ImageAnnotator from '../components/ImageAnnotator';

type Point = [number, number];

const BoardCreate: React.FC = () => {
  const [name, setName] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [annotations, setAnnotations] = useState<Point[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setImageFile(file);
    setAnnotations([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!imageFile || annotations.length < 3) {
      alert(
        'Please upload an image and annotate at least three points to define the board.',
      );
      return;
    }

    setIsLoading(true);

    const reader = new FileReader();
    reader.readAsDataURL(imageFile);
    reader.onloadend = async () => {
      const base64Image = reader.result?.toString().split(',')[1];

      try {
        await API.post('/wall', {
          name,
          image: base64Image,
          wall_annotations: annotations,
        });

        navigate('/');
      } catch (error) {
        console.error('Error creating wall:', error);
      } finally {
        setIsLoading(false);
      }
    };
  };

  const handleResetAnnotations = () => {
    setAnnotations([]);
  };

  return (
    <div className="board-create">
      <h1>Create New Board</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Board Name:</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Board Image:</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            required
          />
        </div>
        {imageFile && (
          <div>
            <p>
              Click on the image to annotate the boards's polygon. Click "Finish Annotation" when done.
            </p>
            <ImageAnnotator
              imageFile={imageFile}
              annotations={annotations}
              setAnnotations={setAnnotations}
            />
            <p>{annotations.length} point(s) added.</p>
            <button type="button" onClick={handleResetAnnotations}>
              Reset Annotations
            </button>
          </div>
        )}
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating Board...' : 'Create Board'}
        </button>
      </form>
    </div>
  );
};

export default BoardCreate;
