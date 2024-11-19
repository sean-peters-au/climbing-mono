#!/bin/bash

set -a
source /opt/betaboard-camera/.env
set +a

ffmpeg -f v4l2 -framerate 10 -video_size 640x480 -i /dev/video0 \
    -c:v h264_v4l2m2m -b:v 500k \
    -hls_time 2 -hls_list_size 3 -hls_flags delete_segments \
    /var/www/html/stream/stream.m3u8