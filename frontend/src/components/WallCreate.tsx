import React, { useState, useRef } from 'react';
import API from '../services/api';
import { useNavigate } from 'react-router-dom';

const WallCreate: React.FC = () => {
  const [name, setName] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageDataUrl, setImageDataUrl] = useState<string | null>(null);
  const [annotations, setAnnotations] = useState<{ x: number; y: number }[]>([]);
  const navigate = useNavigate();
  const imageContainerRef = useRef<HTMLDivElement>(null);

  // Handle image file selection
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setImageFile(file);

    if (file) {
      // Convert image file to data URL for display
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageDataUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setImageDataUrl(null);
      setAnnotations([]);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!imageFile || annotations.length !== 4) {
      alert('Please upload an image and annotate the four corners of the wall.');
      return;
    }

    // Convert image to base64
    const reader = new FileReader();
    reader.readAsDataURL(imageFile);
    reader.onloadend = async () => {
      const base64Image = reader.result?.toString().split(',')[1];

      await API.post('/wall', {
        name,
        image: base64Image,
        wall_annotations: annotations,
      });

      navigate('/');
    };
  };

  // Handle image clicks for annotation
  const handleImageClick = (e: React.MouseEvent) => {
    if (annotations.length >= 4) return;

    const rect = imageContainerRef.current?.getBoundingClientRect();
    if (!rect) return;

    const img = imageContainerRef.current?.querySelector('img');
    if (!img) return;

    const scaleX = img.naturalWidth / img.clientWidth;
    const scaleY = img.naturalHeight / img.clientHeight;

    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    setAnnotations([...annotations, { x, y }]);
  };

  // Reset annotations
  const handleResetAnnotations = () => {
    setAnnotations([]);
  };

  return (
    <div>
      <h1>Create New Wall</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Wall Name:</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div>
          <label>Wall Image:</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            required
          />
        </div>
        {imageDataUrl && (
          <div>
            <h3>
              Click on the Four Corners of the Wall Image (Order: Top-Left,
              Top-Right, Bottom-Left, Bottom-Right)
            </h3>
            <div
              ref={imageContainerRef}
              style={{ position: 'relative', display: 'inline-block' }}
              onClick={handleImageClick}
            >
              <img
                src={imageDataUrl}
                alt="Wall"
                style={{ maxWidth: '100%', display: 'block' }}
              />
              <svg
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  pointerEvents: 'none',
                }}
                width="100%"
                height="100%"
                viewBox={`0 0 ${
                  imageContainerRef.current?.offsetWidth || 0
                } ${imageContainerRef.current?.offsetHeight || 0}`}
                preserveAspectRatio="none"
              >
                {annotations.map((point, index) => (
                  <circle
                    key={index}
                    cx={point.x * (imageContainerRef.current?.offsetWidth || 0) / (imageContainerRef.current?.querySelector('img')?.naturalWidth || 1)}
                    cy={point.y * (imageContainerRef.current?.offsetHeight || 0) / (imageContainerRef.current?.querySelector('img')?.naturalHeight || 1)}
                    r={5}
                    fill="red"
                  />
                ))}
                {annotations.length === 4 && (
                  <polygon
                    points={annotations
                      .map(
                        (p) =>
                          `${(p.x * (imageContainerRef.current?.offsetWidth || 0)) / (imageContainerRef.current?.querySelector('img')?.naturalWidth || 1)},${
                            (p.y * (imageContainerRef.current?.offsetHeight || 0)) /
                            (imageContainerRef.current?.querySelector('img')?.naturalHeight || 1)
                          }`
                      )
                      .join(' ')}
                    fill="rgba(255,0,0,0.2)"
                    stroke="red"
                    strokeWidth={2}
                  />
                )}
              </svg>
            </div>
            {annotations.length < 4 && (
              <p>Points selected: {annotations.length} / 4</p>
            )}
            {annotations.length === 4 && (
              <p>You have selected all four corners.</p>
            )}
            <button type="button" onClick={handleResetAnnotations}>
              Reset Annotations
            </button>
          </div>
        )}
        <button type="submit">Create Wall</button>
      </form>
    </div>
  );
};

export default WallCreate;