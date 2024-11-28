import atexit
import functools
import io
import os
import tempfile
import threading
import time
import typing
import subprocess

import flask
import flask_cors
import libcamera
import picamera2
import picamera2.encoders
import picamera2.outputs


# Global camera lock
_camera_lock = threading.Lock()


class CameraLockTimeoutError(Exception):
    """Exception raised when a lock cannot be acquired within the timeout."""
    pass


def with_camera_lock(timeout: float = 5.0):
    """
    Decorator to acquire the camera lock before executing the function.

    Args:
        timeout (float): Maximum time to wait for the lock in seconds.

    Raises:
        CameraLockTimeoutError: If the lock cannot be acquired within the timeout.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            acquired = _camera_lock.acquire(timeout=timeout)
            if not acquired:
                raise CameraLockTimeoutError(f"Could not acquire camera lock within {timeout} seconds.")
            try:
                return func(*args, **kwargs)
            finally:
                _camera_lock.release()
        return wrapper
    return decorator


def with_camera_init(func):
    """
    Decorator to initialize the camera before executing the function and clean up on exception.

    Args:
        func (callable): The function to decorate.

    Raises:
        Exception: Propagates any exception raised by the decorated function after cleanup.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            self.initialize_camera()
            return func(self, *args, **kwargs)
        except Exception as e:
            self.cleanup_camera()
            raise e
    return wrapper


class CameraManager:
    """Manages camera operations including initialization, streaming, and recording."""
    RESOLUTION = {
        "main": {"size": (1920, 1080)},
        "lores": {"size": (640, 480)},
    }
    FRAMERATE = 30
    RECORDING_BITRATE = 10000000  # 10Mbps for recording
    JPEG_QUALITY = {
        "photo": 100,
        "stream": 60,
    }
    MAX_RECORDING_DURATION = 180  # 3 minutes in seconds
    FLIP_CAMERA = True  # Set to True if camera is mounted upside down

    def __init__(self):
        self.camera_lock = threading.Lock()
        self.camera: typing.Optional[picamera2.Picamera2] = None
        self.streaming = False
        self.recording = False
        self.encoder: typing.Optional[picamera2.encoders.H264Encoder] = None
        self.recording_start_time: typing.Optional[float] = None
        self.current_recording_file: typing.Optional[str] = None
        self.duration_thread: typing.Optional[threading.Thread] = None
        self.video_config: typing.Optional[picamera2.Configuration] = None
        self.photo_config: typing.Optional[picamera2.Configuration] = None

    @with_camera_lock(timeout=5.0)
    def initialize_camera(self) -> None:
        """Initialize the camera if not already initialized."""
        if self.camera is None:
            try:
                self.camera = picamera2.Picamera2()

                # Configure camera with standard resolution and framerate
                self.video_config = self.camera.create_video_configuration(
                    main=self.RESOLUTION["main"],
                    lores=self.RESOLUTION["lores"],
                    display="lores",
                    transform=libcamera.Transform(vflip=self.FLIP_CAMERA, hflip=self.FLIP_CAMERA) if self.FLIP_CAMERA else None,
                    controls={"FrameRate": self.FRAMERATE}
                )
                self.photo_config = self.camera.create_still_configuration(
                    main=self.RESOLUTION["main"],
                    transform=libcamera.Transform(vflip=self.FLIP_CAMERA, hflip=self.FLIP_CAMERA) if self.FLIP_CAMERA else None,
                    controls={
                        "AfMode": libcamera.controls.AfModeEnum.Auto,
                        "LensPosition": 0.0,
                        "AeEnable": True,
                        "AwbEnable": True,
                        "Sharpness": 2.0,
                        "NoiseReductionMode": libcamera.controls.draft.NoiseReductionModeEnum.HighQuality,
                    }
                )
                self.camera.configure(self.video_config)
                self.camera.start()
                time.sleep(2)  # Camera warm-up time
            except Exception as e:
                self.cleanup_camera()
                raise e

    @with_camera_lock(timeout=5.0)
    def cleanup_camera(self) -> None:
        """Clean up camera resources."""
        if self.camera:
            try:
                if self.recording and self.encoder:
                    self.encoder.stop()
                self.camera.stop()
                self.camera.close()
            except:
                pass  # Best effort cleanup
            finally:
                # Clean up any leftover recording file
                if self.current_recording_file and os.path.exists(self.current_recording_file):
                    try:
                        os.unlink(self.current_recording_file)
                    except:
                        pass  # Best effort cleanup
                self.camera = None
                self.encoder = None
                self.streaming = False
                self.recording = False
                self.current_recording_file = None
                self.recording_start_time = None

    @with_camera_lock(timeout=5.0)
    def check_recording_duration(self) -> None:
        """Check recording duration and stop if exceeded maximum."""
        while self.recording and self.recording_start_time:
            current_duration = time.time() - self.recording_start_time
            if current_duration >= self.MAX_RECORDING_DURATION:
                with self.camera_lock:
                    try:
                        if self.recording and self.encoder:
                            self.camera.stop_recording()
                            self.recording = False
                            self.recording_start_time = None

                            # Revert to streaming configuration
                            self.camera.stop()
                            self.camera.configure(self.camera.create_video_configuration(
                                main={"size": (640, 480)},
                                lores={"size": (320, 240)},
                                display="lores"
                            ))
                            self.camera.start()
                    except Exception as e:
                        self.cleanup_camera()
                        raise e
                break
            time.sleep(1)  # Check every second

    @with_camera_init
    @with_camera_lock(timeout=5.0)
    def capture_photo(self) -> io.BytesIO:
        """Capture a single photo and return it as a BytesIO stream."""
        stream = io.BytesIO()
        self.camera.switch_mode(self.photo_config)
        time.sleep(0.5) # Allow focus to adjust
        self.camera.options["quality"] = self.JPEG_QUALITY["photo"]
        self.camera.capture_file(stream, format='jpeg')
        stream.seek(0)
        self.camera.switch_mode(self.video_config)
        return stream

    @with_camera_init
    @with_camera_lock(timeout=5.0)
    def start_recording(self) -> None:
        """Start recording video to a file."""
        if not self.recording:
            temp_file = tempfile.NamedTemporaryFile(suffix='.h264', delete=False)
            self.current_recording_file = temp_file.name
            temp_file.close()

            self.encoder = picamera2.encoders.H264Encoder(
                bitrate=self.RECORDING_BITRATE,
                repeat=False,
                iperiod=10
            )
            self.encoder.frame_skip_count = 10
            self.camera.start_recording(self.encoder, self.current_recording_file)
            self.recording = True
            self.recording_start_time = time.time()

            self.duration_thread = threading.Thread(target=self.check_recording_duration)
            self.duration_thread.daemon = True
            self.duration_thread.start()

    @with_camera_init
    @with_camera_lock(timeout=5.0)
    def stop_recording(self) -> io.BytesIO:
        """Stop recording and return the recorded video as BytesIO."""
        if self.recording and self.current_recording_file:
            self.camera.stop_recording()
            self.recording = False

            with open(self.current_recording_file, 'rb') as f:
                video_data = f.read()

            os.unlink(self.current_recording_file)
            self.current_recording_file = None

            return io.BytesIO(video_data)
        else:
            raise RuntimeError("No recording in progress")

    @with_camera_init
    @with_camera_lock(timeout=5.0)
    def start_streaming(self) -> typing.Generator[bytes, None, None]:
        """
        Start streaming video feed using H264 encoder.
        
        Returns:
            Generator yielding video stream data chunks.
        """
        try:
            # Create FFmpeg command for MPEGTS stream
            ffmpeg_cmd = (
                "ffmpeg -f h264 -i pipe:0 "
                "-c:v copy "
                "-f mpegts pipe:1"
            )
            
            # Start FFmpeg process
            ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Create encoder and output
            self.encoder = picamera2.encoders.H264Encoder(
                bitrate=1000000,  # 1Mbps
                repeat=False,
                iperiod=15,
            )
            output = picamera2.outputs.FileOutput(ffmpeg_process.stdin)
            
            # Start the encoder
            self.camera.start_encoder(self.encoder, output)
            
            try:
                while True:
                    data = ffmpeg_process.stdout.read(4096)  # Increased buffer size
                    if not data:
                        break
                    yield data
            finally:
                self.stop_streaming()
                ffmpeg_process.terminate()
                ffmpeg_process.wait(timeout=5.0)
        except Exception as e:
            self.cleanup_camera()
            raise e

    @with_camera_init
    @with_camera_lock(timeout=5.0)
    def stop_streaming(self) -> None:
        """Stop streaming video feed."""
        if self.encoder:
            self.camera.stop_encoder()


app = flask.Flask(__name__)
flask_cors.CORS(app)
camera_manager = CameraManager()


@app.errorhandler(Exception)
def handle_error(e: Exception) -> flask.Response:
    """Handle unexpected exceptions."""
    return flask.Response(str(e), status=500)


@app.route('/capture_photo', methods=['GET'])
def capture_photo() -> flask.Response:
    """Capture a single photo and return it."""
    try:
        stream = camera_manager.capture_photo()
        return flask.send_file(stream, mimetype='image/jpeg')
    except CameraLockTimeoutError as e:
        return flask.Response(str(e), status=400)


@app.route('/video_feed')
def video_feed() -> flask.Response:
    """Stream video feed using H264."""
    try:
        stream = camera_manager.start_streaming()

        @flask.after_this_request
        def cleanup(response):
            try:
                camera_manager.stop_streaming()
            except Exception as e:
                app.logger.error(f"Error during stream cleanup: {e}")
            return response

        return flask.Response(
            stream,
            mimetype='video/mp2t'
        )
    except CameraLockTimeoutError as e:
        return flask.Response(str(e), status=400)


@app.route('/start_recording', methods=['POST'])
def start_recording() -> flask.Response:
    """Start recording video to a file."""
    try:
        camera_manager.start_recording()
        return 'Recording started', 200
    except CameraLockTimeoutError as e:
        return flask.Response(str(e), status=400)


@app.route('/stop_recording', methods=['POST'])
def stop_recording() -> flask.Response:
    """Stop recording and return the recorded video."""
    try:
        video_data = camera_manager.stop_recording()
        return flask.send_file(
            video_data,
            mimetype='video/h264'
        )
    except CameraLockTimeoutError as e:
        return flask.Response(str(e), status=400)


@app.route('/shutdown', methods=['POST'])
def shutdown() -> flask.Response:
    """Shutdown the camera and clean up resources."""
    try:
        camera_manager.cleanup_camera()
        return 'Camera shutdown', 200
    except CameraLockTimeoutError as e:
        return flask.Response(str(e), status=400)


atexit.register(camera_manager.cleanup_camera)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)