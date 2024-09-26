// src/components/ImageAnnotator.tsx
import React, { useRef, useEffect } from 'react';
import './ImageAnnotator.css';

interface Props {
  imageFile: File;
  annotations: [number, number][];
  setAnnotations: React.Dispatch<React.SetStateAction<[number, number][]>>;
}

const ImageAnnotator: React.FC<Props> = ({ imageFile, annotations, setAnnotations }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = imgRef.current;
    const canvas = canvasRef.current;

    if (img && canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          draw();
        };
        img.src = URL.createObjectURL(imageFile);
      }
    }

    return () => {
      if (img) {
        URL.revokeObjectURL(img.src);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageFile]);

  useEffect(() => {
    draw();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [annotations]);

  const draw = () => {
    const canvas = canvasRef.current;
    const img = imgRef.current;

    if (canvas && img) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Draw image
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        // Draw annotations
        if (annotations.length > 0) {
          ctx.fillStyle = 'rgba(0, 255, 0, 0.3)'; // Semi-transparent green
          ctx.strokeStyle = 'rgba(0, 255, 0, 0.8)'; // Less transparent for stroke
          ctx.lineWidth = 2;

          ctx.beginPath();
          ctx.moveTo(annotations[0][0], annotations[0][1]);
          for (let i = 1; i < annotations.length; i++) {
            ctx.lineTo(annotations[i][0], annotations[i][1]);
          }
          ctx.closePath();
          ctx.fill();
          ctx.stroke();

          // Draw points
          annotations.forEach((point) => {
            ctx.beginPath();
            ctx.arc(point[0], point[1], 5, 0, 2 * Math.PI);
            ctx.fillStyle = 'red';
            ctx.fill();
          });
        }
      }
    }
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (canvas) {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;

      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;

      setAnnotations([...annotations, [x, y]]);
    }
  };

  const handleFinishAnnotation = () => {
    // Optional: Perform any final actions when annotation is finished
    // For now, simply log the annotations
    console.log('Annotation finished:', annotations);
  };

  return (
    <div className="image-annotator">
      <canvas ref={canvasRef} onClick={handleCanvasClick} />
      <img ref={imgRef} alt="To annotate" style={{ display: 'none' }} />
      <button type="button" onClick={handleFinishAnnotation}>
        Finish Annotation
      </button>
    </div>
  );
};

export default ImageAnnotator;