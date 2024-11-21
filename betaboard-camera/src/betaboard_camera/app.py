import threading
import time

import flask
import cv2

import betaboard_camera.utils.config as config_utils


app = flask.Flask(__name__)
app.config.from_object(config_utils.Config)

# Global camera instance and lock
camera_lock = threading.Lock()
camera = None
recording = False
streaming = False
output_frame = None
video_writer = None


def initialize_camera():
    global camera
    if camera is None:
        camera_type = app.config['CAMERA_TYPE']
        if camera_type == 'opencv':
            camera_index = app.config['CAMERA_INDEX']
            camera = cv2.VideoCapture(camera_index)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            time.sleep(2)
        else:
            raise ValueError("Unsupported camera type")
    else:
        # Test if the camera is opened
        if not camera.isOpened():
            camera.open(app.config['CAMERA_INDEX'])

def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None

@app.route('/capture_photo')
def capture_photo():
    with camera_lock:
        initialize_camera()
        ret, frame = camera.read()
        if not ret:
            return 'Failed to capture image', 500
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            return 'Failed to encode image', 500
        frame_bytes = buffer.tobytes()
        return flask.Response(frame_bytes, mimetype='image/jpeg')

def gen_frames():
    global output_frame, streaming
    while True:
        with camera_lock:
            if not streaming:
                break
            if output_frame is None:
                continue
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', output_frame)
            if not ret:
                continue
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.05)  # Adjust frame rate as needed

def camera_loop():
    global camera, output_frame, recording, video_writer, streaming
    while True:
        with camera_lock:
            if not streaming and not recording:
                break
            if camera is None:
                continue
            ret, frame = camera.read()
            if not ret:
                continue
            output_frame = frame.copy()
            if recording and video_writer is not None:
                video_writer.write(frame)
        time.sleep(0.01)

@app.route('/video_feed')
def video_feed():
    global streaming
    with camera_lock:
        initialize_camera()
        streaming = True
    threading.Thread(target=camera_loop).start()
    return flask.Response(
        gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame',
    )

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording, video_writer
    with camera_lock:
        initialize_camera()
        if not recording:
            timestamp = int(time.time())
            filename = f'recording_{timestamp}.avi'
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 20.0
            frame_size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                          int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            video_writer = cv2.VideoWriter(filename, fourcc, fps, frame_size)
            recording = True
            if not streaming:
                # Start the camera loop if not already running
                threading.Thread(target=camera_loop).start()
            return 'Recording started', 200
        else:
            return 'Recording already in progress', 400

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, video_writer
    with camera_lock:
        if recording:
            recording = False
            video_writer.release()
            video_writer = None
            return 'Recording stopped', 200
        else:
            return 'No recording in progress', 400

@app.route('/shutdown', methods=['POST'])
def shutdown():
    global streaming, recording
    with camera_lock:
        streaming = False
        recording = False
        release_camera()
    return 'Camera shutdown', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)