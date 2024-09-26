// src/utils/holdUtils.ts
import { Hold } from '../types';

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
  mask: boolean[][]
): string => {
  const [x, y, width, height] = bbox;
  const borderThickness = 2; // Define the border thickness

  // Expand canvas size to accommodate the border
  const canvasWidth = width + borderThickness * 2;
  const canvasHeight = height + borderThickness * 2;

  const canvas = document.createElement('canvas');
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  const context = canvas.getContext('2d');
  if (!context) return '';

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

  return canvas.toDataURL();
};