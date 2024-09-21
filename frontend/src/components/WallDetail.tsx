import React, { useEffect, useState, useRef } from 'react';
import API from '../services/api';
import { useParams } from 'react-router-dom';
import { Wall } from '../types';
import ClimbList from './ClimbList';
import ClimbCreate from './ClimbCreate';

const WallDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [wall, setWall] = useState<Wall | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHolds, setSelectedHolds] = useState<string[]>([]);
  const [showAllHolds, setShowAllHolds] = useState<boolean>(false);
  const [holdImages, setHoldImages] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const fetchWall = async () => {
      try {
        const response = await API.get(`/wall/${id}`);
        setWall(response.data);
      } catch (err) {
        setError('Failed to fetch wall data.');
        console.error('Error fetching wall:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWall();
  }, [id]);

  useEffect(() => {
    if (wall) {
      generateHoldImages(wall.holds);
    }
  }, [wall]);

  const generateHoldImages = (holds: any[]) => {
    const images: { [key: string]: string } = {};
    holds.forEach((hold) => {
      const holdId = hold.id;
      const { bbox, mask } = hold;
      const imageDataUrl = createHoldImage(bbox, mask);
      images[holdId] = imageDataUrl;
    });
    setHoldImages(images);
  };

  const createHoldImage = (bbox: number[], mask: boolean[][]): string => {
    const [x, y, width, height] = bbox;
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d');
    if (!context) return '';

    // Draw the mask onto the canvas
    const imageData = context.createImageData(width, height);
    for (let row = 0; row < mask.length; row++) {
      for (let col = 0; col < mask[0].length; col++) {
        const index = (row * width + col) * 4;
        if (mask[row][col]) {
          // Set pixel to semi-transparent red
          imageData.data[index] = 255;     // R
          imageData.data[index + 1] = 0;   // G
          imageData.data[index + 2] = 0;   // B
          imageData.data[index + 3] = 128; // A (0-255)
        } else {
          // Leave pixel transparent
          imageData.data[index + 3] = 0;
        }
      }
    }
    context.putImageData(imageData, 0, 0);

    // Draw the border around the mask
    context.strokeStyle = 'black';
    context.lineWidth = 2;
    context.beginPath();
    for (let row = 0; row < mask.length; row++) {
      for (let col = 0; col < mask[0].length; col++) {
        if (mask[row][col]) {
          // Check if the current pixel is on the border
          const isBorder = 
            !mask[row - 1]?.[col] || !mask[row + 1]?.[col] || 
            !mask[row]?.[col - 1] || !mask[row]?.[col + 1];
          if (isBorder) {
            context.moveTo(col, row);
            context.lineTo(col + 1, row);
            context.lineTo(col + 1, row + 1);
            context.lineTo(col, row + 1);
            context.lineTo(col, row);
          }
        }
      }
    }
    context.stroke();

    return canvas.toDataURL();
  };

  const handleHoldClick = (holdId: string) => {
    setSelectedHolds((prevSelected) =>
      prevSelected.includes(holdId)
        ? prevSelected.filter((id) => id !== holdId)
        : [...prevSelected, holdId]
    );
  };

  if (loading) {
    return <div>Loading wall details...</div>;
  }

  if (error || !wall) {
    return <div>{error || 'Wall not found.'}</div>;
  }

  return (
    <div>
      <h1>{wall.name}</h1>
      <button onClick={() => setShowAllHolds(!showAllHolds)}>
        {showAllHolds ? 'Hide All Holds' : 'Show All Holds'}
      </button>
      <div style={{ position: 'relative', display: 'inline-block' }}>
        <img
          src={wall.image}
          alt={wall.name}
          style={{ maxWidth: '100%', display: 'block' }}
        />
        <svg
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            cursor: 'pointer',
          }}
          width="100%"
          height="100%"
          viewBox={`0 0 ${wall.width} ${wall.height}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {wall.holds.map((hold, index) => {
            const holdId = hold.id;
            const isSelected = selectedHolds.includes(holdId);
            const shouldDisplay = showAllHolds || isSelected;
            if (!shouldDisplay) return null;

            const [x, y, width, height] = hold.bbox;

            return (
              <image
                key={holdId}
                href={holdImages[holdId]}
                x={x}
                y={y}
                width={width}
                height={height}
                opacity={isSelected ? 0.8 : 0.5}
                onClick={(e) => {
                  e.stopPropagation();
                  handleHoldClick(holdId);
                }}
              />
            );
          })}
        </svg>
      </div>
      <h2>Climbs</h2>
      <ClimbList climbs={wall.routes} />
      <ClimbCreate wallId={wall.id} selectedHolds={selectedHolds} />
      <button onClick={() => setSelectedHolds([])}>Reset Hold Selection</button>
    </div>
  );
};

export default WallDetail;