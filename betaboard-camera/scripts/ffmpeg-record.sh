#!/bin/bash

# Load environment variables
set -a
source /home/pi/.env
set +a

# Directory to store video segments
OUTPUT_DIR="$VIDEO_DIR"
mkdir -p "$OUTPUT_DIR"

# FFmpeg command to record video in segments, overwriting older files
ffmpeg -f v4l2 -framerate 30 -video_size 1280x720 -i /dev/video0 \
  -c:v h264_omx -b:v 2M \
  -f segment -segment_time "$VIDEO_SEGMENT_DURATION" -segment_wrap "$VIDEO_SEGMENT_NUMBER" -reset_timestamps 1 \
  "$OUTPUT_DIR/output%03d.mp4"