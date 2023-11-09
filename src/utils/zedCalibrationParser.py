"""
Requires ZED Calibration File (.conf), e.g. from https://www.stereolabs.com/developers/calib/ or ZED SDK

Usage:
    python zedCalibrationParser.py <calibration_file_path> <resolution> <output_path>
""" 

import re
import json
import argparse
import numpy as np
from pathlib import Path
import cv2

resolution_dict = {
    '2K': (2208, 1242),
    'FHD': (1920, 1080),
    'HD': (1280, 720),
    'VGA': (672, 376)
}

def parse_calibration(file_path, resolution):
    with open(file_path, 'r') as file:
        calibration_data = file.read()

    # Define the camera names based on the resolution
    left_cam_name = f'LEFT_CAM_{resolution}'
    right_cam_name = f'RIGHT_CAM_{resolution}'

    # Extract the camera data using a regular expression
    left_camera_data = re.findall(rf'\[{left_cam_name}\](.*?)\n\n', calibration_data, re.DOTALL)
    right_camera_data = re.findall(rf'\[{right_cam_name}\](.*?)\n\n', calibration_data, re.DOTALL)
    stereo_data = re.findall(r'\[STEREO\](.*?)\n\n', calibration_data, re.DOTALL)
    
    if not left_camera_data or not right_camera_data or not stereo_data:
        raise ValueError("Camera data not found for the given resolution or stereo data missing.")

    # Convert the extracted data into dictionaries
    left_camera_dict = dict(re.findall(r'(\w+)=([-\d.e]+)', left_camera_data[0]))
    right_camera_dict = dict(re.findall(r'(\w+)=([-\d.e]+)', right_camera_data[0]))
    stereo_dict = dict(re.findall(r'(\w+)=([-\d.e]+)', stereo_data[0]))

    # Convert the Rodrigues vector to a rotation matrix
    rod_vec = np.array([
        float(stereo_dict.get(f'RX_{resolution}', 0.0)),
        float(stereo_dict.get(f'CV_{resolution}', 0.0)),
        float(stereo_dict.get(f'RZ_{resolution}', 0.0))
    ])
    R2, _ = cv2.Rodrigues(rod_vec)

    # Prepare the output dictionary
    output_dict = {
        "baseline": float(stereo_dict.get('Baseline', 0.0)),
        "leftCameraMatrix": [
            [float(left_camera_dict.get('fx', 0.0)), 0.0, float(left_camera_dict.get('cx', 0.0))],
            [0.0, float(left_camera_dict.get('fy', 0.0)), float(left_camera_dict.get('cy', 0.0))],
            [0.0, 0.0, 1.0]
        ],
        "rightCameraMatrix": [
            [float(right_camera_dict.get('fx', 0.0)), 0.0, float(right_camera_dict.get('cx', 0.0))],
            [0.0, float(right_camera_dict.get('fy', 0.0)), float(right_camera_dict.get('cy', 0.0))],
            [0.0, 0.0, 1.0]
        ],
        "leftDistCoeffs": [
            float(left_camera_dict.get('k1', 0.0)),
            float(left_camera_dict.get('k2', 0.0)),
            float(left_camera_dict.get('k3', 0.0)),
            float(left_camera_dict.get('k4', 0.0))
        ],
        "rightDistCoeffs": [
            float(right_camera_dict.get('k1', 0.0)),
            float(right_camera_dict.get('k2', 0.0)),
            float(right_camera_dict.get('k3', 0.0)),
            float(right_camera_dict.get('k4', 0.0))
        ],
        "R1": [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ],
        "R2": R2.tolist(),
        "T1": [0, 0, 0],
        "T2": [
            float(stereo_dict.get('Baseline', 0.0))/1000.0,
            float(stereo_dict.get('TY', 0.0))/1000.0,
            float(stereo_dict.get('TZ', 0.0))/1000.0
        ],
        # Assuming VGA resolution as a placeholder
        "imageWidth": resolution_dict[resolution][0],
        "imageHeight": resolution_dict[resolution][1]
    }

    return output_dict

def main():
    parser = argparse.ArgumentParser(description='Parse calibration data to JSON format.')
    parser.add_argument('file_path', type=str, help='Path to the calibration file.')
    parser.add_argument('resolution', type=str, choices=['2K', 'FHD', 'HD', 'VGA'], help='Desired resolution.')
    parser.add_argument('output_path', type=str, help='Output path for the JSON file.')

    args = parser.parse_args()

    # Parse the calibration data
    calibration_data = parse_calibration(args.file_path, args.resolution)

    # Write the calibration data to the output JSON file
    with open(args.output_path, 'w') as outfile:
        json.dump(calibration_data, outfile, indent=4)

    print(f'Calibration data has been written to {args.output_path}')

if __name__ == "__main__":
    main()
