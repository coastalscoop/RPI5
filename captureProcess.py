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
    #cam.start_preview(Preview.QTGL)
    cam.start()
    cameras.append(cam)

# Additional sleep to ensure cameras are ready
sleep(5)

output_folder = "data/BlastBeach"  # Specify the desired output folder
os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist

# Save the first image
for camera_num, cam in enumerate(cameras, 1):
    # Capture the image
    first_image = cam.capture_array()

    # Convert the image to RGB color space
    first_image_rgb = cv2.cvtColor(first_image, cv2.COLOR_BGR2RGB)

    # Save the first image using the specified filename format
    filename = format_timestamp(get_epoch_time(), camera_num)
    prefix = filename[:-11]
    cv2.imwrite(os.path.join(output_folder, filename), first_image_rgb)
    print(f"First image for Camera {camera_num} saved as {filename}")

# Initialize variables for average image, brightest image, darkest image, and variance image
average_images = [None] * len(cameras)
brightest_images = [None] * len(cameras)
darkest_images = [None] * len(cameras)
variance_images = [None] * len(cameras)
image_counts = [0] * len(cameras)

start_time = monotonic()

# Use the correct key for duration from the configuration
start_time = monotonic()
duration_seconds = config_data["camera_settings"][0]["duration"]

while monotonic() - start_time < duration_seconds:
    epoch_time = get_epoch_time()

    for camera_num, cam in enumerate(cameras, 1):
        capture_start_time = monotonic()

        # Capture the image
        image = cam.capture_array()

        # Convert the image to RGB color space
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image to create a timex image
        if average_images[camera_num - 1] is None:
            average_images[camera_num - 1] = image_rgb.astype(np.float64)
        else:
            average_images[camera_num - 1] += (image_rgb.astype(np.float64) - average_images[camera_num - 1]) / (
                    image_counts[camera_num - 1] + 1)

        # Update brightest image
        if brightest_images[camera_num - 1] is None:
            brightest_images[camera_num - 1] = image_rgb
        else:
            brightest_images[camera_num - 1] = np.maximum(brightest_images[camera_num - 1], image_rgb)

        # Update darkest image
        if darkest_images[camera_num - 1] is None:
            darkest_images[camera_num - 1] = image_rgb
        else:
            darkest_images[camera_num - 1] = np.minimum(darkest_images[camera_num - 1], image_rgb)

        # Update the variance image using NumPy's method
        img_as_float = image_rgb.astype(np.float64)
        if variance_images[camera_num - 1] is None:
            variance_images[camera_num - 1] = np.zeros_like(img_as_float)

        variance_images[camera_num - 1] += (img_as_float - average_images[camera_num - 1]) * (
                img_as_float - average_images[camera_num - 1])

        # Record the epoch at which the image array was captured
        captured_epochs[camera_num - 1].append(epoch_time)

        # Increment image count
        image_counts[camera_num - 1] += 1

        # Calculate the time taken for the capture
        time_taken = monotonic() - capture_start_time

        # If the capture time is less than 1 second, wait the remaining time
        if time_taken < 1:
            time.sleep(1 - time_taken)

# Calculate the final variance images
for camera_num in range(len(cameras)):
    variance_images[camera_num] /= image_counts[camera_num]

# Process and save the final timex, brightest, darkest, and variance images
for camera_num, (timex_image, brightest_image, darkest_image, variance_image, image_count) in enumerate(
        zip(average_images, brightest_images, darkest_images, variance_images, image_counts), 1):
    if timex_image is not None:
        # Process the final timex image (replace this with your processing logic)
        final_timex_image = timex_image.astype(np.uint8)

        # Save the final timex image (converted to RGB)
        timex_filename = f"{prefix}c{camera_num}.timex.jpg"
        cv2.imwrite(os.path.join(output_folder, timex_filename), final_timex_image)
        print(f"Final timex image for Camera {camera_num} saved as {timex_filename}")

        # Process the brightest image
        if brightest_image is not None:
            # Save the corrected brightest image (converted to RGB)
            brightest_filename = f"{prefix}c{camera_num}.brightest.jpg"
            cv2.imwrite(os.path.join(output_folder, brightest_filename), brightest_image)
            print(f"Corrected brightest image for Camera {camera_num} saved as {brightest_filename}")

        # Process the darkest image
        if darkest_image is not None:
            # Save the corrected darkest image (converted to RGB)
            darkest_filename = f"{prefix}c{camera_num}.darkest.jpg"
            cv2.imwrite(os.path.join(output_folder, darkest_filename), darkest_image)
            print(f"Corrected darkest image for Camera {camera_num} saved as {darkest_filename}")

        # Scale the variance values as per the provided mechanics
        if variance_image is not None:
            min_var = variance_image.min()
            max_var = variance_image.max()
            scaled_variance_image = ((variance_image - min_var) / (max_var - min_var) * 255).astype(np.uint8)

            # Save the scaled variance image
            variance_filename = f"{prefix}c{camera_num}.variance.jpg"
            cv2.imwrite(os.path.join(output_folder, variance_filename), scaled_variance_image)
            print(f"Scaled variance image for Camera {camera_num} saved as {variance_filename}")

# Stop cameras
for cam in cameras:
    cam.stop()
    cam.stop_preview()

# Print the captured epochs for each camera along with image count and gaps
for camera_num, epochs in enumerate(captured_epochs, 1):
    print(f"\nCaptured epochs for Camera {camera_num}:")
    image_count = len(epochs)  # Count the number of images captured
    print(f"Number of images captured: {image_count}")

    if image_count > 1:
        # Calculate and print min, median, and max gaps between subsequent images
        time_gaps = [epochs[i + 1] - epochs[i] for i in range(image_count - 1)]
        min_gap = min(time_gaps)
        median_gap = median(time_gaps)
        max_gap = max(time_gaps)

        print(f"Minimum gap between subsequent images: {min_gap}")
        print(f"Median gap between subsequent images: {median_gap}")
        print(f"Maximum gap between subsequent images: {max_gap}")

    for epoch in epochs:
        print(epoch)
