import os
import subprocess
import tempfile
import time

import flask
import typing


def process_video_request(start_time: int, end_time: int) -> bytes:
    """
    Process the video request by concatenating the relevant video segments.

    Args:
        start_time (int): Start time of the requested video segment (Unix timestamp).
        end_time (int): End time of the requested video segment (Unix timestamp).

    Returns:
        bytes: The concatenated video data.

    Raises:
        ValueError: If the requested segments are not available.
        Exception: If an error occurs during video processing.
    """
    app = flask.current_app
    logger = app.logger

    segments_needed = _get_segments_for_time_range(start_time, end_time)
    if not segments_needed:
        logger.warning("Requested segments are not available after waiting.")
        raise ValueError('Requested video segments are not yet available. Please try again shortly.')

    output_data = _create_video_from_segments(segments_needed, start_time, end_time)
    if output_data is None:
        logger.error("Error occurred during video creation.")
        raise Exception('Error concatenating video segments.')

    logger.info("Successfully processed video request")
    return output_data


def _get_segments_for_time_range(start_time: int, end_time: int) -> typing.List[typing.Tuple[int, str]]:
    """
    Retrieve the list of video segments that cover the requested time range.

    Args:
        start_time (int): The requested start time as a Unix timestamp.
        end_time (int): The requested end time as a Unix timestamp.

    Returns:
        List[Tuple[int, str]]: A list of tuples containing segment start time and path.
    """
    app = flask.current_app
    video_dir = app.config['VIDEO_DIR']
    segment_duration = app.config['VIDEO_SEGMENT_DURATION']

    max_wait_time = 3.0  # Maximum time to wait for segments (in seconds)
    wait_interval = 0.5  # Interval between checks (in seconds)
    total_wait_time = 0.0

    while total_wait_time <= max_wait_time:
        segments = _get_all_segments(video_dir)
        segments_needed = _select_required_segments(segments, start_time, end_time, segment_duration)

        if segments_needed:
            return segments_needed

        time.sleep(wait_interval)
        total_wait_time += wait_interval

    return []


def _get_all_segments(video_dir: str) -> typing.List[typing.Tuple[int, str]]:
    """
    Retrieve all available video segments from the video directory.

    Args:
        video_dir (str): The directory where video segments are stored.

    Returns:
        List[Tuple[int, str]]: A list of tuples containing segment start time and path.
    """
    segments = []
    for filename in os.listdir(video_dir):
        if filename.startswith('segment_') and filename.endswith('.mp4'):
            try:
                timestamp_str = filename[len('segment_'):-len('.mp4')]
                segment_time = int(timestamp_str)
                segment_path = os.path.join(video_dir, filename)
                segments.append((segment_time, segment_path))
            except ValueError:
                continue  # Skip files with invalid timestamp
    segments.sort(key=lambda x: x[0])
    return segments


def _select_required_segments(
    segments: typing.List[typing.Tuple[int, str]],
    start_time: int,
    end_time: int,
    segment_duration: int
) -> typing.List[typing.Tuple[int, str]]:
    """
    Select the segments that cover the requested time range.

    Args:
        segments (List[Tuple[int, str]]): Available video segments.
        start_time (int): Requested start time.
        end_time (int): Requested end time.
        segment_duration (int): Duration of each segment.

    Returns:
        List[Tuple[int, str]]: Segments that cover the requested time range.
    """
    current_time = int(time.time())
    segments_needed = []

    for segment_time, segment_path in segments:
        segment_end_time = segment_time + segment_duration
        if segment_end_time <= start_time:
            continue  # Segment ends before the requested start time
        elif segment_time >= end_time:
            break  # Segment starts after the requested end time
        elif segment_end_time > current_time:
            continue  # Exclude segments that are still being recorded
        else:
            segments_needed.append((segment_time, segment_path))

    return segments_needed


def _create_video_from_segments(
    segments_needed: typing.List[typing.Tuple[int, str]],
    start_time: int,
    end_time: int
) -> typing.Optional[bytes]:
    """
    Concatenate the selected video segments and return the video data.

    Args:
        segments_needed (List[Tuple[int, str]]): Segments to be concatenated.
        start_time (int): Requested start time.
        end_time (int): Requested end time.

    Returns:
        Optional[bytes]: The concatenated video data, or None if an error occurred.
    """
    app = flask.current_app
    logger = app.logger

    try:
        concat_file_path = _create_concat_file(segments_needed)
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

        trim_start_offset = start_time - segments_needed[0][0]
        total_duration = end_time - start_time

        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file_path,
            '-ss', str(trim_start_offset),
            '-t', str(total_duration),
            '-c', 'copy',
            output_path
        ]

        subprocess.run(
            ffmpeg_cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(output_path, 'rb') as f:
            output_data = f.read()

        return output_data

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {' '.join(ffmpeg_cmd)}")
        logger.error(f"FFmpeg error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error during video creation: {e}")
        return None
    finally:
        _clean_up_temporary_files([concat_file_path, output_path])


def _create_concat_file(segments_needed: typing.List[typing.Tuple[int, str]]) -> str:
    """
    Create a temporary concat file listing the video segments.

    Args:
        segments_needed (List[Tuple[int, str]]): Segments to be concatenated.

    Returns:
        str: The path to the concat file.
    """
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as concat_file:
        for _, segment in segments_needed:
            abs_path = os.path.abspath(segment)
            concat_file.write(f"file '{abs_path}'\n")
        return concat_file.name


def _clean_up_temporary_files(file_paths: typing.List[str]) -> None:
    """
    Remove temporary files created during video processing.

    Args:
        file_paths (List[str]): List of file paths to remove.
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            continue  # Ignore errors during cleanup