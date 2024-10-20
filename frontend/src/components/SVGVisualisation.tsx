import React from 'react';
import { Box } from '@mui/material';
import { SensorReading, Hold } from '../types';

type SVGVisualizationProps = {
  sensorData: SensorReading[];
  holds: Hold[];
};

const SVGVisualization: React.FC<SVGVisualizationProps> = ({ sensorData, holds }) => {
  const svgWidth = 800;
  const svgHeight = 600;

  // Aggregate forces by hold
  const holdForces = sensorData.map((data) => {
    const totalForces = data.forces.reduce(
      (acc, force) => ({
        x: acc.x + force.x,
        y: acc.y + force.y,
      }),
      { x: 0, y: 0 }
    );
    return {
      hold_id: data.hold_id,
      x: totalForces.x / data.forces.length,
      y: totalForces.y / data.forces.length,
    };
  });

  return (
    <Box mt={2}>
      <svg width={svgWidth} height={svgHeight} style={{ border: '1px solid #ccc' }}>
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="0"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="red" />
          </marker>
        </defs>

        {/* Draw Holds */}
        {holds.map((hold) => {
          const [x1, y1, x2, y2] = hold.bbox;
          const centerX = (x1 + x2) / 2;
          const centerY = (y1 + y2) / 2;
          return (
            <circle key={hold.id} cx={centerX} cy={centerY} r={10} fill="blue" />
          );
        })}

        {/* Draw Forces */}
        {holdForces.map((forceData) => {
          const hold = holds.find((h) => h.id === forceData.hold_id);
          if (!hold) return null;

          const [x1, y1, x2, y2] = hold.bbox;
          const centerX = (x1 + x2) / 2;
          const centerY = (y1 + y2) / 2;

          const magnitude = Math.sqrt(forceData.x ** 2 + forceData.y ** 2);
          const scale = 0.1; // Adjust this value for scaling the vectors
          const endX = centerX + forceData.x * scale;
          const endY = centerY - forceData.y * scale; // Negative because SVG y-axis is downwards

          return (
            <g key={forceData.hold_id}>
              <line
                x1={centerX}
                y1={centerY}
                x2={endX}
                y2={endY}
                stroke="red"
                strokeWidth={2}
                markerEnd="url(#arrowhead)"
              />
              <text x={endX + 5} y={endY - 5} fontSize="12" fill="black">
                {magnitude.toFixed(2)} N
              </text>
            </g>
          );
        })}
      </svg>
    </Box>
  );
};

export default SVGVisualization;