# Camera Service

A service providing video capabilities for the BetaBoard system. Currently implemented for Raspberry Pi cameras.

## Features

### Photo Capture
- Provides still images for wall setup and hold detection
- Requirements:
  - Fast response time for interactive use
  - Consistent image quality
- Endpoint: `/capture_photo`

### Live Streaming
- Real-time video feed for remote viewing
- Requirements:
  - Low latency for interactive use
  - Stable continuous streaming
- Endpoint: `/video_feed`

### Video Recording
- Records climbs for later analysis
- Requirements:
  - Reliable long-duration recording
  - Synchronized with sensor data collection
- Endpoints: `/start_recording`, `/stop_recording`

## Technical Details

- HTTP API built with Flask
- Hardware-accelerated video processing
- Thread-safe design supporting concurrent operations:
  - Simultaneous streaming and recording
  - Photo capture during streaming
- Graceful resource cleanup on shutdown

## Supported Hardware

Currently supports:
- Raspberry Pi Camera Module
- Raspberry Pi Zero W / Raspberry Pi 4