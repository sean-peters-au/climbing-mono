// src/utils/holdUtils.ts
import { Hold, HoldAnnotationPlayback, HoldVector, Playback, PlaybackData } from '../../../types';

const OVERLAY_FRAME_RATE = 100;

export const generateHoldImages = (holds: Hold[]): { [key: string]: string } => {
  const images: { [key: string]: string } = {};
  holds.forEach((hold) => {
    const holdId = hold.id;
    const { bbox, mask } = hold;
    const imageDataUrl = createHoldImage(bbox, mask);
    images[holdId] = imageDataUrl;
  });
  return images;
};

export const createHoldImage = (
  bbox: number[],
  mask?: boolean[][]
): string => {
  const width = bbox[2];
  const height = bbox[3];
  const borderThickness = 2; // Define the border thickness

  // Expand canvas size to accommodate the border
  const canvasWidth = width + borderThickness * 2;
  const canvasHeight = height + borderThickness * 2;

  const canvas = document.createElement('canvas');
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  const context = canvas.getContext('2d');
  if (!context) return '';

  if (mask && mask.length && mask[0].length) {
    // Function to create ImageData from mask with specified color
    const createMaskImageData = (color: { r: number; g: number; b: number }): ImageData => {
      const imageData = context.createImageData(width, height);
      for (let row = 0; row < height; row++) {
        for (let col = 0; col < width; col++) {
          const index = (row * width + col) * 4;
          if (mask[row][col]) {
            imageData.data[index] = color.r;     // R
            imageData.data[index + 1] = color.g; // G
            imageData.data[index + 2] = color.b; // B
            imageData.data[index + 3] = 200;     // A (fully opaque)
          } else {
            imageData.data[index + 3] = 0;       // Transparent
          }
        }
      }
      return imageData;
    };

    // Create the border mask image data
    const borderColor = { r: 0, g: 0, b: 0 }; // Black
    const borderImageData = createMaskImageData(borderColor);

    // Create the fill mask image data
    const fillColor = { r: 255, g: 0, b: 0 }; // Red
    const fillImageData = createMaskImageData(fillColor);

    // Create offscreen canvas for border mask
    const borderMaskCanvas = document.createElement('canvas');
    borderMaskCanvas.width = width;
    borderMaskCanvas.height = height;
    const borderMaskContext = borderMaskCanvas.getContext('2d');
    if (!borderMaskContext) return '';
    borderMaskContext.putImageData(borderImageData, 0, 0);

    // Create offscreen canvas for fill mask
    const fillMaskCanvas = document.createElement('canvas');
    fillMaskCanvas.width = width;
    fillMaskCanvas.height = height;
    const fillMaskContext = fillMaskCanvas.getContext('2d');
    if (!fillMaskContext) return '';
    fillMaskContext.putImageData(fillImageData, 0, 0);

    // Draw the border by drawing the border mask multiple times with offsets
    for (let dx = -borderThickness; dx <= borderThickness; dx++) {
      for (let dy = -borderThickness; dy <= borderThickness; dy++) {
        if (dx === 0 && dy === 0) continue; // Skip center position
        context.drawImage(
          borderMaskCanvas,
          0,
          0,
          width,
          height,
          borderThickness + dx,
          borderThickness + dy,
          width,
          height
        );
      }
    }

    // Now draw the fill mask at the center
    context.drawImage(
      fillMaskCanvas,
      0,
      0,
      width,
      height,
      borderThickness,
      borderThickness,
      width,
      height
    );
  } else {
    // Fallback: draw a rectangle using the bbox dimensions
    // Set border color
    context.strokeStyle = 'black';
    context.lineWidth = borderThickness;

    // Set fill color
    context.fillStyle = 'red';

    // Draw filled rectangle with border
    context.fillRect(
      borderThickness,
      borderThickness,
      width,
      height
    );
    context.strokeRect(
      borderThickness,
      borderThickness,
      width,
      height
    );
  }

  return canvas.toDataURL();
};

/*
 * Returns an array of hold numbers in order of their appearance on the board
 */
export const getHoldNumbers = (holds: Hold[]): HoldAnnotationPlayback[] => {
  // First sort the holds by their y-coordinate (and then x-coordinate if there are ties)
  const sortedHolds = holds.sort((a, b) => {
    if (a.bbox[1] !== b.bbox[1]) return b.bbox[1] - a.bbox[1];
    return b.bbox[0] - a.bbox[0];
  });

  const holdNumbers: HoldAnnotationPlayback[] = [];
  sortedHolds.forEach((hold, index) => {
    holdNumbers.push({
      hold_id: hold.id,
      frequency: 10,
      data: {
        annotation: index + 1,
      },
    });
  });

  return holdNumbers;
};

/*
 * Interpolates playback data to a target frame rate
 */
export const interpolatePlayback = <T extends PlaybackData>(playback: Playback<T>): Playback<T> => {
  const targetFrameRate = OVERLAY_FRAME_RATE;
  const sourceFrameRate = playback.frequency;
  const interpolationFactor = targetFrameRate / sourceFrameRate;

  if (!Array.isArray(playback.data)) {
    return playback;
  }

  let interpolatedData: T[];
  if (interpolationFactor === 1) {
    interpolatedData = playback.data;
  } else if (interpolationFactor > 1) {
    interpolatedData = upsamplePlayback(playback.data, interpolationFactor);
  } else {
    interpolatedData = downsamplePlayback(playback.data, interpolationFactor);
  }

  return {
    hold_id: playback.hold_id,
    frequency: targetFrameRate,
    data: interpolatedData,
  };
};

const upsamplePlayback = <T>(playbackData: T[], interpolationFactor: number): T[] => {
  if (playbackData.length < 2) return playbackData;

  const interpolatedData: T[] = [];

  for (let i = 0; i < playbackData.length - 1; i++) {
    const currentData = playbackData[i];
    const nextData = playbackData[i + 1];

    // Add the current vector
    interpolatedData.push(currentData);

    // Create interpolated vectors between current and next
    for (let j = 1; j < interpolationFactor; j++) {
      const t = j / interpolationFactor;
      interpolatedData.push(interpolate(currentData, nextData, t));
    }
  }

  // Add the last vector
  interpolatedData.push(playbackData[playbackData.length - 1]);

  return interpolatedData;
};

const downsamplePlayback = <T>(playbackData: T[], interpolationFactor: number): T[] => {
  if (playbackData.length < 2) return playbackData;

  const downsampledData: T[] = [];
  const step = Math.round(1 / interpolationFactor);

  for (let i = 0; i < playbackData.length; i += step) {
    downsampledData.push(playbackData[i]);
  }

  return downsampledData;
};

const interpolate = <T>(currentData: T, nextData: T, t: number): T => {
  if (isHoldVector(currentData) && isHoldVector(nextData)) {
    return {
      x: currentData.x + (nextData.x - currentData.x) * t,
      y: currentData.y + (nextData.y - currentData.y) * t,
    } as T;
  } else if (isHoldAnnotation(currentData) && isHoldAnnotation(nextData)) {
    return {
      annotation: currentData.annotation + (nextData.annotation - currentData.annotation) * t,
    } as T;
  }
  return currentData; // fallback
};

// Type guards
const isHoldVector = (data: any): data is HoldVector => {
  return typeof data?.x === 'number' && typeof data?.y === 'number';
};

const isHoldAnnotation = (data: any): data is { annotation: number } => {
  return typeof data?.annotation === 'number';
};
