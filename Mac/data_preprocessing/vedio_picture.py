import subprocess
import time
from datetime import datetime
from moviepy.editor import VideoFileClip
import threading
import cv2
import random
import os
import glob
import numpy as np
import tkinter as tk
from tkinter import ttk
import os
from ML_learning.MobileNetV2 import ML_detect_trash
from tensorflow.keras.preprocessing.image import load_img, img_to_array

output_folder = "/Users/jichanglong/Desktop/cameradata/"
output_folder2 = "/Users/jichanglong/Desktop/camerascreen/"

# Define the Mosquitto publish function
def publish_to_mosquitto(value):
    cmd = [
        "mosquitto_pub",
        "-h", "172.16.1.166",
        "-t", "predict",
        "-m", str(value)
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Published successfully: {value}")
    except subprocess.CalledProcessError as e:
        print(f"Publish failed: {e}")

def calculate_brightness(img_path):
    """Calculate the average brightness of an image"""
    img = load_img(img_path)
    img_array = img_to_array(img)
    # Convert to grayscale from RGB
    grayscale = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
    return np.mean(grayscale)

def detect_trash(img_path, reference_brightness = 150):
    """Detect if there is trash in the image"""
    brightness = calculate_brightness(img_path)
    if brightness < reference_brightness:
        return 1  # Output 1 indicates trash present
    else:
        return 0  # Output 0 indicates no trash

def execute():
    while True:
        try:
            images = glob.glob(output_folder2 + "*.jpg")
            if images:
                images = sorted(images, key=os.path.getctime)
                earliest_image = images[0]
                result = detect_trash(earliest_image)
                #result = ML_detect_trash(earliest_image)
                publish_to_mosquitto(result)
                os.remove(earliest_image)  # Remove the image
            time.sleep(1)
        except Exception as e:
            print(f"Execution error: {e}")
            time.sleep(1)

def record_video():
    local_folder = output_folder
    hdfs_destination = "/test/"

    while True:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f"{current_time}.mp4"
        full_output_path = f"{local_folder}/{output_file}"
        record_duration = 10

        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "avfoundation",
            "-i", "1",
            "-t", str(record_duration),
            "-vf", "fps=30,crop=800:1400:100:250",
            full_output_path
        ]

        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print(f"Recording completed, saved as {output_file}")

            # Upload to Hadoop
            hadoop_cmd = [
                "hadoop", "fs", "-copyFromLocal",
                full_output_path,
                hdfs_destination
            ]

            process = subprocess.Popen(hadoop_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print(f"Video file {output_file} successfully uploaded to Hadoop.")
                # Delete the local file
                os.remove(full_output_path)
                print(f"Local video file {output_file} has been deleted.")
            else:
                print(f"Upload to Hadoop failed, error message: {stderr.decode('utf-8')}")
        else:
            print(f"Recording failed, error message: {stderr.decode('utf-8')}")

        time.sleep(5)

def capture_screenshots():
    while True:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f"{current_time}.jpg"
        screenshot_cmd = [
            "ffmpeg",
            "-f", "avfoundation",
            "-i", "1",
            "-vf", f"fps=1,crop=800:1400:100:250",
            "-vframes", "1",
            f"{output_folder2}{output_file}"
        ]

        try:
            subprocess.run(screenshot_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

            print(f"Screenshot completed, saved as {output_file}")
            time.sleep(3)
        except subprocess.CalledProcessError as e:
            print(f"Screenshot failed, error message: {e}")

if __name__ == "__main__":
    video_thread = threading.Thread(target=record_video)
    screenshot_thread = threading.Thread(target=capture_screenshots)
    execute_thread = threading.Thread(target=execute)

    video_thread.start()
    screenshot_thread.start()
    execute_thread.start()
