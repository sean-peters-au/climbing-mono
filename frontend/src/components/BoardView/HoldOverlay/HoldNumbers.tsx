import React, { useContext } from 'react';
import { getHoldNumbers } from './helpers';
import { BoardViewContext } from '../BoardViewContext';

const HoldNumbers: React.FC = () => {
  const { selectedRoute } = useContext(BoardViewContext)!;
  const holds = selectedRoute?.holds || [];
  const holdNumbers = getHoldNumbers(holds);

  return (
    <>
      {holds.map((hold) => {
        const [x, y, width, height] = hold.bbox;
        const textX = x + width;
        const textY = y + height;

        return (
          <text
            key={`number-${hold.id}`}
            x={textX}
            y={textY}
            fontSize="2.5rem"
            textAnchor="start"
            dominantBaseline="hanging"
            style={{
              fill: 'white',
              stroke: 'black',
              strokeWidth: '0.4rem',
              paintOrder: 'stroke fill', // Ensures stroke appears behind fill
              userSelect: 'none',
            }}
          >
            {holdNumbers[hold.id]}
          </text>
        );
      })}
    </>
  );
};

export default HoldNumbers;