import React, { useContext } from 'react';
import { BoardViewContext } from '../BoardViewContext';

export const HoldAnnotations: React.FC = () => {
  const { holds, playbackAnnotations, isPlaying, currentFrame } = useContext(BoardViewContext)!;

  if (!isPlaying || playbackAnnotations.length === 0) return null;


  return (
    <>
    {playbackAnnotations.map((playback) => {
        const hold = holds.find((h) => h.id === playback.hold_id);
        if (!hold) return null;
        const [x, y, width, height] = hold.bbox;

        // If the annotation is an array, get the current frame's annotation
        // Otherwise, the annotation is static over all frames
        const annotation = Array.isArray(playback.data) ? playback.data[currentFrame] : playback.data;

        return (
          <text
            key={hold.id}
            x={x + width}
            y={y + height}
            fontSize="2.5rem"
            fill="white"
            stroke="black"
            strokeWidth="1.5"
          >
            {annotation.annotation.toFixed(2)}
          </text>
        );
      })}
    </>
  );
};