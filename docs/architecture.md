# Architecture

![Architecture Plan](architecture-plan.png)

## System Overview

BetaBoard is a distributed system for managing climbing walls, analyzing climber performance, and
providing real-time feedback. The system consists of several specialized services that work together
to provide a complete climbing analysis platform.

## Core Services

### Frontend

A React/TypeScript application providing the user interface. Key design choices:
- TypeScript for type safety
- React Query + Context for clear separation of server/UI state

### Backend

A Flask application serving as the central coordinator. Key design choices:
- Python selected for strength in data analysis and visualization
- Simple REST API design with clear separation of concerns
- Marshmallow, SQLAlchemy, Plotly...

### Image Processing Service

A separate service for computationally expensive image operations. Key design choices:
- Designed for serverless deployment (AWS Lambda)
- Isolated from main backend to allow independent scaling
- Handles operations like hold detection and image segmentation

### Postgres Database

Primary data store for the system. Stores:
- Wall configurations and images
- Route definitions
- Sensor configurations
- Climbing recordings and analysis results

## Edge Devices

### Sensors

Small, networked devices (Raspberry Pi Picos) attached to climbing holds. Design choices:
- Simple HTTP API for data retrieval
- Static IP configuration for reliability
- One-time registration with backend
- Real-time force/pressure data collection

### Camera

Raspberry Pi Zero W providing video services. Capabilities:
- Live streaming for real-time viewing
- Recording for post-climb analysis
- Still image capture for wall setup
- Integration with recording system for synchronized playback

#### Features & Implementation

**Photo Capture**
- Provides high-quality still images for wall setup and hold detection
- Requirements:
  - Fast capture response time (<500ms)
  - JPEG format for web compatibility
  - Resolution: 640x480
- Implementation:
  - REST endpoint using PiCamera's capture method
  - Uses video port for faster capture
  - Thread-safe camera access via locks

**Live Streaming**
- Real-time video feed for remote viewing
- Requirements:
  - Low latency (<200ms)
  - Efficient bandwidth usage
  - Browser compatibility
- Implementation:
  - MJPEG stream over HTTP
  - Frame-by-frame delivery using multipart responses
  - Configurable frame rate (default: 20fps)
  - Thread-safe frame capture

**Video Recording**
- Records climbs for later analysis and playback
- Requirements:
  - Synchronized with sensor data
  - Efficient storage format
  - Reliable long-duration recording
- Implementation:
  - H.264 hardware encoding
  - Separate recording stream (splitter port)
  - Timestamped filenames for easy correlation
  - Automatic cleanup on shutdown

**Technical Details**
- Flask-based HTTP API
- PiCamera for hardware-accelerated capture
- Thread-safe design for concurrent operations
- Graceful shutdown handling
- Configurable resolution and frame rates

## Integration Points

### Data Flow

1. **Wall Management**
   - Frontend → Backend: Board and route management
   - Backend → Image Processing: Hold detection
   - Backend → S3: Image storage

2. **Climb Recording**
   - Sensors → Backend: Real-time sensor data
   - Camera → Backend: Video stream/recording
   - Backend → Frontend: Synchronized playback

3. **Analysis**
   - Backend: Combines sensor data with video
   - Backend → Frontend: Analysis results and visualizations

### Key Considerations

- **Deployment**: Currently runs in Docker Compose locally, designed for cloud deployment
- **Scaling**: Image processing isolated for cost-effective scaling
- **Real-time**: Sensor and video data must be precisely synchronized
- **Storage**: Efficient handling of large video and sensor datasets