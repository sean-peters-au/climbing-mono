import atexit
import io
import threading
import time
import typing
import os
import tempfile

import flask
import flask_cors
import libcamera
import picamera2
import picamera2.encoders
import picamera2.outputs


# Constants
MAX_RECORDING_DURATION = 180  # 3 minutes in seconds
FLIP_CAMERA = True  # Set to True if camera is mounted upside down
RESOLUTION = {
    "main": {"size": (1920, 1080)},  # 1080p for consistent FOV
    "lores": {"size": (640, 480)},   # Keep lores for internal usage
}
FRAMERATE = 30

# Quality settings for different modes
RECORDING_BITRATE = 10000000  # 10Mbps for recording
JPEG_QUALITY = {
    "photo": 95,    # High quality for photos
    "stream": 60    # Lower quality for streaming
}

app = flask.Flask(__name__)
flask_cors.CORS(app)

# Global camera instance and lock
camera_lock = threading.Lock()
camera: typing.Optional[picamera2.Picamera2] = None
streaming = False
recording = False
encoder: typing.Optional[picamera2.encoders.H264Encoder] = None

# Add recording start time and max duration constants
recording_start_time: typing.Optional[float] = None

# Add to global variables at top of file
current_recording_file: typing.Optional[str] = None

def initialize_camera() -> None:
    """Initialize the camera if not already initialized."""
    global camera
    if camera is None:
        try:
            camera = picamera2.Picamera2()
            
            # Configure camera with standard resolution and framerate
            config = camera.create_video_configuration(
                main=RESOLUTION["main"],
                lores=RESOLUTION["lores"],
                display="lores",
                transform=libcamera.Transform(vflip=FLIP_CAMERA, hflip=FLIP_CAMERA) if FLIP_CAMERA else None,
                controls={"FrameRate": FRAMERATE}
            )
            camera.configure(config)
            camera.start()
            time.sleep(2)  # Camera warm-up time
        except Exception as e:
            cleanup_camera()
            raise e


def cleanup_camera() -> None:
    """Clean up camera resources."""
    global camera, streaming, recording, encoder, current_recording_file
    if camera:
        try:
            if recording and encoder:
                encoder.stop()
            camera.stop()
            camera.close()
        except:
            pass  # Best effort cleanup
        finally:
            # Clean up any leftover recording file
            if current_recording_file and os.path.exists(current_recording_file):
                try:
                    os.unlink(current_recording_file)
                except:
                    pass  # Best effort cleanup
            camera = None
            encoder = None
            streaming = False
            recording = False
            current_recording_file = None


def check_recording_duration() -> None:
    """Check recording duration and stop if exceeded maximum."""
    global recording, recording_start_time
    while recording and recording_start_time:
        current_duration = time.time() - recording_start_time
        if current_duration >= MAX_RECORDING_DURATION:
            with camera_lock:
                try:
                    if recording and encoder:
                        camera.stop_recording()
                        recording = False
                        recording_start_time = None
                        
                        # Revert to streaming configuration
                        camera.stop()
                        camera.configure(camera.create_video_configuration(
                            main={"size": (640, 480)},
                            lores={"size": (320, 240)},
                            display="lores"
                        ))
                        camera.start()
                except Exception as e:
                    cleanup_camera()
                    raise e
            break
        time.sleep(1)  # Check every second


@app.route('/capture_photo', methods=['GET'])
def capture_photo() -> flask.Response:
    """Capture a single photo and return it."""
    print("Capturing photo")
    with camera_lock:
        try:
            print("Capturing photo: Initializing camera")
            initialize_camera()
            stream = io.BytesIO()
            # Set high quality for photos
            camera.options["quality"] = JPEG_QUALITY["photo"]
            camera.capture_file(stream, format='jpeg')
            stream.seek(0)
            return flask.send_file(stream, mimetype='image/jpeg')
        except Exception as e:
            cleanup_camera()
            raise e


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()
        self.active = True  # Add flag to track streaming status

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

    def stop(self):
        self.active = False
        with self.condition:
            self.condition.notify_all()


@app.after_request
def after_request(response):
    """Handle cleanup after client disconnects."""
    cleanup_camera()
    return response


@app.route('/video_feed')
def video_feed() -> flask.Response:
    """Stream video feed using H264."""
    with camera_lock:
        try:
            initialize_camera()
            
            # Create a pipe for streaming
            output = picamera2.outputs.FfmpegOutput(
                "-f h264 -preset ultrafast -tune zerolatency "
                "-c:v libx264 -b:v 1000k "
                "-x264-params keyint=15:min-keyint=15 "
                "-f mpegts pipe:1",
                pts=True
            )
            
            # Start streaming with H264 encoder
            encoder = picamera2.encoders.H264Encoder()
            camera.start_encoder(encoder, output)
            
            @flask.after_this_request
            def cleanup(response):
                camera.stop_encoder()
                return response
            
            return flask.Response(
                output.start(),
                mimetype='video/mp2t'
            )
            
        except Exception as e:
            cleanup_camera()
            raise e


@app.route('/start_recording', methods=['POST'])
def start_recording() -> typing.Tuple[str, int]:
    """Start recording video to a file."""
    global recording, encoder, recording_start_time, current_recording_file
    
    with camera_lock:
        try:
            initialize_camera()
            if not recording:
                temp_file = tempfile.NamedTemporaryFile(suffix='.h264', delete=False)
                current_recording_file = temp_file.name
                temp_file.close()
                
                # Reduced bitrate for smoother recording
                encoder = picamera2.encoders.H264Encoder(
                    bitrate=RECORDING_BITRATE,
                    repeat=False,
                    iperiod=10
                )
                encoder.frame_skip_count = 10
                camera.start_recording(encoder, current_recording_file)
                recording = True
                recording_start_time = time.time()
                
                duration_thread = threading.Thread(target=check_recording_duration)
                duration_thread.daemon = True
                duration_thread.start()
                
                return 'Recording started', 200
            else:
                return 'Recording already in progress', 400
        except Exception as e:
            cleanup_camera()
            if current_recording_file and os.path.exists(current_recording_file):
                os.unlink(current_recording_file)
            raise e


@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    """Stop recording and return the recorded video."""
    global recording, current_recording_file
    
    with camera_lock:
        try:
            if recording and current_recording_file:
                camera.stop_recording()
                recording = False
                
                try:
                    # Read the video file
                    with open(current_recording_file, 'rb') as f:
                        video_data = f.read()
                    
                    # Delete the temporary file
                    os.unlink(current_recording_file)
                    current_recording_file = None
                    
                    return flask.send_file(
                        io.BytesIO(video_data),
                        mimetype='video/h264'
                    )
                except Exception as e:
                    if current_recording_file and os.path.exists(current_recording_file):
                        os.unlink(current_recording_file)
                    raise e
            else:
                return 'No recording in progress', 400
        except Exception as e:
            cleanup_camera()
            raise e


@app.route('/shutdown', methods=['POST'])
def shutdown() -> typing.Tuple[str, int]:
    """Shutdown the camera and clean up resources."""
    with camera_lock:
        cleanup_camera()
    return 'Camera shutdown', 200


# Ensure cleanup on process termination
atexit.register(cleanup_camera)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)