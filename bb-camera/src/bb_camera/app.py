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


class BaseCameraManager:
    """Base class for camera operations with common configuration."""
    
    RESOLUTION = {
        "main": {"size": (1920, 1080)},
        "lores": {"size": (640, 480)},
    }
    FRAMERATE = 30
    FLIP_CAMERA = True

    def __init__(self):
        self.camera: typing.Optional[picamera2.Picamera2] = None
        
    def __enter__(self):
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def initialize(self):
        """Initialize camera with basic configuration."""
        if self.camera is None:
            self.camera = picamera2.Picamera2()
            time.sleep(2)  # Camera warm-up

    def cleanup(self):
        """Clean up camera resources."""
        if self.camera:
            try:
                self.camera.stop()
                self.camera.close()
            finally:
                self.camera = None


class PhotoCameraManager(BaseCameraManager):
    """Specialized manager for taking high-quality photos."""
    
    def __init__(self):
        super().__init__()
        self.photo_config = None

    def initialize(self):
        super().initialize()
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
        self.camera.configure(self.photo_config)
        self.camera.start()

    def capture(self) -> io.BytesIO:
        """Capture a single high-quality photo."""
        stream = io.BytesIO()
        time.sleep(0.5)  # Give the camera time to focus
        self.camera.capture_file(stream, format='jpeg')
        stream.seek(0)
        return stream 


class StreamingCameraManager(BaseCameraManager):
    """Specialized manager for MJPEG streaming."""
    
    JPEG_QUALITY = 60

    def __init__(self):
        super().__init__()
        self.video_config = None
        self.jpeg_encoder = None
        self.streaming = False

    def initialize(self):
        super().initialize()
        self.video_config = self.camera.create_video_configuration(
            main=self.RESOLUTION["main"],
            lores=self.RESOLUTION["lores"],
            display="lores",
            transform=libcamera.Transform(vflip=self.FLIP_CAMERA, hflip=self.FLIP_CAMERA) if self.FLIP_CAMERA else None,
            controls={"FrameRate": self.FRAMERATE}
        )
        self.camera.configure(self.video_config)
        self.camera.start()
        time.sleep(0.5)  # Give camera time to settle
        self.jpeg_encoder = picamera2.encoders.JpegEncoder(q=self.JPEG_QUALITY)

    def cleanup(self):
        """Ensure proper cleanup sequence."""
        try:
            if self.streaming:
                self.camera.stop_recording()
                self.streaming = False
            if self.jpeg_encoder:
                self.camera.stop_encoder()
                self.jpeg_encoder = None
        except:
            pass  # Best effort cleanup
        finally:
            super().cleanup()

    def stream(self) -> typing.Generator[bytes, None, None]:
        """Stream MJPEG video."""
        class StreamingOutput(io.BufferedIOBase):
            def __init__(self):
                self.frame = None
                self.condition = threading.Condition()

            def write(self, buf):
                with self.condition:
                    self.frame = buf
                    self.condition.notify_all()

        output = StreamingOutput()
        try:
            self.camera.start_recording(self.jpeg_encoder, picamera2.outputs.FileOutput(output))
            self.streaming = True

            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            raise
        finally:
            self.cleanup()


class RecordingCameraManager(BaseCameraManager):
    """Specialized manager for H264/MP4 recording."""
    
    RECORDING_BITRATE = 10000000  # 10Mbps
    MAX_DURATION = 180  # 3 minutes

    def __init__(self):
        super().__init__()
        self.video_config = None
        self.h264_encoder = None
        self.current_file = None
        self.start_time = None

    def initialize(self):
        super().initialize()
        self.video_config = self.camera.create_video_configuration(
            main=self.RESOLUTION["main"],
            transform=libcamera.Transform(vflip=self.FLIP_CAMERA, hflip=self.FLIP_CAMERA) if self.FLIP_CAMERA else None,
            controls={"FrameRate": self.FRAMERATE}
        )
        self.camera.configure(self.video_config)
        self.camera.start()
        time.sleep(0.5)  # Give camera time to settle
        
        self.h264_encoder = picamera2.encoders.H264Encoder(
            bitrate=self.RECORDING_BITRATE,
            repeat=False,
            iperiod=10
        )
        self.h264_encoder.frame_skip_count = 10

    def cleanup(self):
        if self.h264_encoder:
            try:
                self.camera.stop_recording()
            except:
                pass
        if self.current_file and os.path.exists(self.current_file):
            try:
                os.unlink(self.current_file)
            except:
                pass
        super().cleanup()

    def start(self) -> None:
        """Start recording to a temporary file."""
        if not self.camera or not self.h264_encoder:
            raise RuntimeError("Camera not properly initialized")

        temp_file = tempfile.NamedTemporaryFile(suffix='.h264', delete=False)
        self.current_file = temp_file.name
        temp_file.close()

        print(f"Starting recording to {self.current_file}")  # Debug print
        self.camera.start_recording(self.h264_encoder, self.current_file)
        self.start_time = time.time()

    def stop(self) -> io.BytesIO:
        """Stop recording and return the video as MP4."""
        if not self.current_file:
            raise RuntimeError("No recording in progress")

        self.camera.stop_recording()
        
        # Convert to MP4
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as mp4_file:
            mp4_path = mp4_file.name

        try:
            subprocess.run([
                'ffmpeg',
                '-i', self.current_file,
                '-c:v', 'copy',
                '-f', 'mp4',
                '-y',
                mp4_path
            ], check=True)

            with open(mp4_path, 'rb') as f:
                video_data = f.read()

            os.unlink(self.current_file)
            os.unlink(mp4_path)
            self.current_file = None
            self.start_time = None

            return io.BytesIO(video_data)
        except Exception as e:
            if os.path.exists(mp4_path):
                os.unlink(mp4_path)
            raise e

class CameraLockTimeoutError(Exception):
    """Exception raised when a lock cannot be acquired within the timeout."""
    pass

class CameraLock:
    """Context manager for camera access."""
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self._lock = threading.Lock()

    def __enter__(self):
        acquired = self._lock.acquire(timeout=self.timeout)
        if not acquired:
            raise CameraLockTimeoutError(f"Could not acquire camera lock within {self.timeout} seconds.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()


app = flask.Flask(__name__)
flask_cors.CORS(app)
camera_lock = CameraLock()


@app.errorhandler(Exception)
def handle_error(e: Exception) -> flask.Response:
    """Handle unexpected exceptions."""
    return flask.Response(str(e), status=500)


@app.route('/capture_photo', methods=['GET'])
def capture_photo() -> flask.Response:
    """Capture a single photo and return it."""
    with camera_lock:
        with PhotoCameraManager() as camera:
            stream = camera.capture()
            return flask.send_file(stream, mimetype='image/jpeg')


@app.route('/video_feed')
def video_feed() -> flask.Response:
    """Stream video feed using MJPEG."""
    camera = None
    with camera_lock:
        try:
            camera = StreamingCameraManager()
            camera.initialize()
            return flask.Response(
                camera.stream(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        except Exception as e:
            if camera:
                camera.cleanup()
            print(f"Error streaming video: {str(e)}")  # Debug print
            return flask.Response(str(e), status=500)


# For recording, we need to maintain the camera instance between start/stop
_recording_camera: typing.Optional[RecordingCameraManager] = None

@app.route('/start_recording', methods=['POST'])
def start_recording() -> flask.Response:
    """Start recording video to a file."""
    global _recording_camera
    
    with camera_lock:
        try:
            if _recording_camera is not None:
                return 'Recording already in progress', 400
                
            _recording_camera = RecordingCameraManager()
            _recording_camera.initialize()
            _recording_camera.start()
            return 'Recording started', 200
        except Exception as e:
            print(f"Error starting recording: {str(e)}")  # Debug print
            if _recording_camera:
                _recording_camera.cleanup()
                _recording_camera = None
            return str(e), 500

@app.route('/stop_recording', methods=['POST'])
def stop_recording() -> flask.Response:
    """Stop recording and return the video."""
    global _recording_camera
    
    with camera_lock:
        if _recording_camera is None:
            return 'No recording in progress', 400
            
        try:
            video_data = _recording_camera.stop()
            return flask.send_file(video_data, mimetype='video/mp4')
        finally:
            _recording_camera.cleanup()
            _recording_camera = None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)