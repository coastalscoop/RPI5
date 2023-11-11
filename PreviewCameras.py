from picamera2 import Picamera2, Preview
from time import sleep, monotonic
import json
import os
from datetime import datetime
import cv2
import numpy as np
import time
from statistics import median

# Read configuration from the JSON file
with open('camera_config.json', 'r') as config_file:
    config_data = json.load(config_file)

def get_epoch_time():
    return datetime.now()

def format_timestamp(epoch_time, camera_num):
    timestamp = epoch_time.timestamp()
    time_str = epoch_time.strftime("%a.%b.%d.%H_%M_%S.GMT.%Y")
    camera_prefix = f"c{camera_num}"
    return f"{timestamp:.6f}.{time_str}.{camera_prefix}.snap.jpg"

# Initialize the cameras list and captured_epochs list
cameras = []
captured_epochs = [[] for _ in range(len(config_data["camera_settings"]))]

for settings in config_data["camera_settings"]:
    cam = Picamera2(settings["camera_id"])
    config = cam.create_preview_configuration({"size": settings["size"]})
    cam.configure(config)
    cam.start_preview(Preview.QTGL)
    cam.start()
    cameras.append(cam)
    
time.sleep(9999)
