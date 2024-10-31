import React, { useContext, useRef, useEffect } from 'react';
import Simplify from 'simplify-js';
import { BoardViewContext } from './BoardViewContext';
import { Point } from '../../types';

const Drawing: React.FC = () => {
  const { isDrawing, wall, setDrawnData } = useContext(BoardViewContext)!;
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [points, setPoints] = React.useState<{ x: number; y: number }[]>([]);
  const [completedPoints, setCompletedPoints] = React.useState<{ x: number; y: number }[]>([]);

  useEffect(() => {
    if (!isDrawing) {
      setPoints([]);
      setCompletedPoints([]);
      setDrawnData(null);
    }
  }, [isDrawing, setDrawnData]);

  const getSVGCoordinates = (e: React.MouseEvent) => {
    const svg = svgRef.current!;
    const point = svg.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;

    const ctm = svg.getScreenCTM();
    if (ctm) {
      const svgPoint = point.matrixTransform(ctm.inverse());
      return { x: svgPoint.x, y: svgPoint.y };
    } else {
      return { x: 0, y: 0 };
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    const { x, y } = getSVGCoordinates(e);
    setPoints([{ x, y }]);
    setCompletedPoints([]);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (points.length > 0) {
      const { x, y } = getSVGCoordinates(e);
      setPoints([...points, { x, y }]);
    }
  };

  const handleMouseUp = () => {
    if (points.length > 2) {
      // Simplify the path to remove extraneous points
      const tolerance = 2; // Adjust this value as needed
      const highQuality = true;
      const simplifiedPoints = Simplify(points, tolerance, highQuality);

      // Ensure the shape is closed
      if (
        simplifiedPoints[0].x !== simplifiedPoints[simplifiedPoints.length - 1].x ||
        simplifiedPoints[0].y !== simplifiedPoints[simplifiedPoints.length - 1].y
      ) {
        simplifiedPoints.push({ ...simplifiedPoints[0] });
      }

      // Calculate bbox as [x, y, width, height]
      const xValues = simplifiedPoints.map((p: Point) => Math.round(p.x));
      const yValues = simplifiedPoints.map((p: Point) => Math.round(p.y));
      const minX = Math.min(...xValues);
      const minY = Math.min(...yValues);
      const width = Math.max(...xValues) - minX + 1;
      const height = Math.max(...yValues) - minY + 1;
      const bbox = [minX, minY, width, height];

      // Create mask using Canvas
      const mask = createMaskFromPolygon(simplifiedPoints, bbox, width, height);

      setDrawnData({ mask, bbox });
      setCompletedPoints(simplifiedPoints); // Save the completed drawing
    }
    setPoints([]); // Clear active drawing points
  };

  const createMaskFromPolygon = (
    polygonPoints: { x: number; y: number }[],
    bbox: number[],
    width: number,
    height: number
  ): boolean[][] => {
    // Create an off-screen canvas
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d')!;
    ctx.fillStyle = '#000';

    // Draw the polygon on the canvas
    ctx.beginPath();
    const firstPoint = polygonPoints[0];
    ctx.moveTo(firstPoint.x - bbox[0], firstPoint.y - bbox[1]);
    for (let i = 1; i < polygonPoints.length; i++) {
      const point = polygonPoints[i];
      ctx.lineTo(point.x - bbox[0], point.y - bbox[1]);
    }
    ctx.closePath();
    ctx.fill();

    // Get pixel data
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;

    // Create mask from pixel data
    const mask: boolean[][] = [];
    for (let y = 0; y < height; y++) {
      const row: boolean[] = [];
      for (let x = 0; x < width; x++) {
        const alpha = data[(y * width + x) * 4 + 3]; // Get alpha value
        row.push(alpha > 0);
      }
      mask.push(row);
    }
    return mask;
  };

  if (!isDrawing) return null;

  return (
    <svg
      ref={svgRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
      viewBox={`0 0 ${wall.width} ${wall.height}`}
      preserveAspectRatio="xMidYMid meet"
    >
      <rect
        width="100%"
        height="100%"
        fill="transparent"
        style={{ pointerEvents: 'all', cursor: 'cell' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      />
      {/* Active drawing line */}
      {points.length > 0 && (
        <polyline
          points={points.map((p) => `${p.x},${p.y}`).join(' ')}
          fill="none"
          stroke="red"
          strokeWidth={2}
        />
      )}
      {/* Completed drawing preview */}
      {completedPoints.length > 0 && (
        <polygon
          points={completedPoints.map((p) => `${p.x},${p.y}`).join(' ')}
          fill="rgba(0, 255, 0, 0.3)"
          stroke="lime"
          strokeWidth={2}
        />
      )}
    </svg>
  );
};

export default Drawing;