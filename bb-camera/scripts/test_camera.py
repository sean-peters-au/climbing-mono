import time
from picamera2 import Picamera2

print("Initializing camera...")
camera = Picamera2()

# Configure a preview and still capture
preview_config = camera.create_preview_configuration()
camera.configure(preview_config)

print("Starting camera...")
camera.start()
time.sleep(2)  # Give time for auto exposure to settle

print("Taking photo...")
camera.capture_file("test_libcamera.jpg")
print("Photo saved to test_libcamera.jpg")

print("Cleaning up...")
camera.stop()
camera.close()
print("Test complete!")