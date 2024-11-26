import io
import tempfile
from typing import Dict, List, Optional

import cv2
import mediapipe as mp
import numpy as np


def analyze_video(video_data: bytes) -> Dict:
    """
    Analyze climbing kinematics from video data using MediaPipe.

    Args:
        video_data: Raw video bytes from the recording.

    Returns:
        Dict containing:
            - frames: List of frame data, each containing:
                - timestamp: Frame timestamp in seconds
                - landmarks: Dict of landmark positions and confidence
            - metadata: Dict containing:
                - frame_count: Total number of frames analyzed
                - duration: Video duration in seconds
                - fps: Frames per second
                - resolution: Video resolution (width, height)
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Write video data to temporary file
    with tempfile.NamedTemporaryFile(suffix='.h264') as temp_video:
        temp_video.write(video_data)
        temp_video.flush()
        
        # Open video file
        cap = cv2.VideoCapture(temp_video.name)
        
        if not cap.isOpened():
            raise ValueError("Failed to open video file")

        try:
            # Get video metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            frames_data = []
            frame_idx = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame with MediaPipe
                results = pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    # Convert landmarks to a more frontend-friendly format
                    landmarks = _process_landmarks(results.pose_landmarks, mp_pose)
                    
                    frames_data.append({
                        'timestamp': frame_idx / fps,
                        'landmarks': landmarks
                    })
                
                frame_idx += 1

            return {
                'frames': frames_data,
                'metadata': {
                    'frame_count': frame_count,
                    'duration': frame_count / fps,
                    'fps': fps,
                    'resolution': {
                        'width': width,
                        'height': height
                    }
                }
            }
        finally:
            cap.release()
            pose.close()


def _process_landmarks(pose_landmarks, mp_pose) -> Dict:
    """
    Convert MediaPipe landmarks to a frontend-friendly format.
    
    Args:
        pose_landmarks: MediaPipe pose landmarks.
        mp_pose: MediaPipe pose module.

    Returns:
        Dict containing normalized coordinates and visibility for each landmark.
    """
    landmarks = {}
    
    # Convert each landmark to a dict with normalized coordinates
    for idx, landmark in enumerate(pose_landmarks.landmark):
        landmark_name = mp_pose.PoseLandmark(idx).name.lower()
        landmarks[landmark_name] = {
            'x': landmark.x,  # Normalized coordinates (0.0 - 1.0)
            'y': landmark.y,
            'z': landmark.z,
            'visibility': landmark.visibility
        }
    
    return landmarks

