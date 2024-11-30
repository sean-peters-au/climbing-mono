// src/utils/holdUtils.ts
import { Hold, HoldAnnotationPlayback, HoldVector, Playback, PlaybackData } from '../../../../types';

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
  const borderThickness = 2; // Updated border thickness to 5 pixels

  // Expand canvas size to accommodate the border
  const canvasWidth = width + borderThickness * 2;
  const canvasHeight = height + borderThickness * 2;

  const canvas = document.createElement('canvas');
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  const context = canvas.getContext('2d');
  if (!context) return '';

  if (mask && mask.length && mask[0].length) {

    // Build a full mask that includes the border with mask values in the center
    const canvasMask = Array.from({ length: canvasHeight }, () => Array(canvasWidth).fill(false));
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        canvasMask[borderThickness + y][borderThickness + x] = mask[y][x];
      }
    }

    // Function to determine if a pixel is around the border of the mask
    // Returns true if is not in the mask but is within borderThickness of the mask
    const isOnMaskBorder = (mask: boolean[][], x: number, y: number): boolean => {
      const onMask = mask[y]?.[x];
      const isWithinBorderThickness = (x: number, y: number): boolean => {
        for (let dx = -borderThickness; dx <= borderThickness; dx++) {
          for (let dy = -borderThickness; dy <= borderThickness; dy++) {
            if (mask[y + dy]?.[x + dx]) return true;
          }
        }
        return false;
      };
      return !onMask && isWithinBorderThickness(x, y);
    };

    // Function to create ImageData from mask with specified color
    const createBorderImageData = (color: { r: number; g: number; b: number }): ImageData => {
      const imageData = context.createImageData(canvasWidth, canvasHeight);
      for (let row = 0; row < canvasHeight; row++) {
        for (let col = 0; col < canvasWidth; col++) {
          const index = (row * canvasWidth + col) * 4;
          if (isOnMaskBorder(canvasMask, col, row)) {
            imageData.data[index] = color.r;     // R
            imageData.data[index + 1] = color.g; // G
            imageData.data[index + 2] = color.b; // B
            imageData.data[index + 3] = 255;     // A (fully opaque)
          } else {
            imageData.data[index + 3] = 0;       // Transparent
          }
        }
      }
      return imageData;
    };

    // Create the border mask image data
    const borderColor = { r: 255, g: 0, b: 0 }; // Red
    const borderImageData = createBorderImageData(borderColor);

    // Create offscreen canvas for border mask
    const borderMaskCanvas = document.createElement('canvas');
    borderMaskCanvas.width = canvasWidth;
    borderMaskCanvas.height = canvasHeight;
    const borderMaskContext = borderMaskCanvas.getContext('2d');
    if (!borderMaskContext) return '';
    borderMaskContext.putImageData(borderImageData, 0, 0);

    // Draw the border by drawing the border mask multiple times with offsets
    for (let dx = -borderThickness; dx <= borderThickness; dx++) {
      for (let dy = -borderThickness; dy <= borderThickness; dy++) {
        if (dx === 0 && dy === 0) continue; // Skip center position
        context.drawImage(
          borderMaskCanvas,
          0,
          0,
          canvasWidth,
          canvasHeight,
          borderThickness + dx,
          borderThickness + dy,
          width,
          height
        );
      }
    }

    // No fill mask is drawn, resulting in only the border being visible
  } else {
    // Fallback: draw a rectangle with only border
    context.strokeStyle = 'red';
    context.lineWidth = borderThickness;

    context.strokeRect(
      borderThickness / 2,
      borderThickness / 2,
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
