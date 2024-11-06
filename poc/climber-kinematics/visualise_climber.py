import sys
import argparse

import cv2
import mediapipe as mediapipe
import numpy


def overlay_skeleton_on_video(video_path: str) -> None:
    """
    Processes the video to perform pose estimation and overlays the skeletal frame.

    Args:
        video_path (str): Path to the input video file.
    """
    mp_drawing = mediapipe.solutions.drawing_utils
    mp_pose = mediapipe.solutions.pose

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        sys.exit(1)

    with mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the BGR image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform pose detection
            results = pose.process(image)

            # Draw the skeleton on the frame
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            # Display the frame
            cv2.imshow('Skeleton Overlay', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Overlay skeletal frame on video and display it."
    )
    parser.add_argument(
        'video_path',
        type=str,
        help='Path to the input video file.'
    )
    args = parser.parse_args()

    if not args.video_path:
        print("Error: No video path provided.")
        sys.exit(1)

    overlay_skeleton_on_video(args.video_path)