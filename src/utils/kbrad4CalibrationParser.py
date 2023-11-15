import argparse
import json
import numpy as np

def parse_calibration(input_file, width, height):
    calibration = {}
    with open(input_file, 'r') as f:
        cal_data = json.load(f)
    
    # Assuming there are two cameras
    left_camera = cal_data['cameras'][0]['calibration']
    right_camera = cal_data['cameras'][1]['calibration']
    
    # Camera matrix
    left_cm = np.array([
        [left_camera['intrinsics']['affine']['fx'], 0, left_camera['intrinsics']['affine']['cx']],
        [0, left_camera['intrinsics']['affine']['fy'], left_camera['intrinsics']['affine']['cy']],
        [0, 0, 1]
    ])
    right_cm = np.array([
        [right_camera['intrinsics']['affine']['fx'], 0, right_camera['intrinsics']['affine']['cx']],
        [0, right_camera['intrinsics']['affine']['fy'], right_camera['intrinsics']['affine']['cy']],
        [0, 0, 1]
    ])
    
    calibration['leftCameraMatrix'] = left_cm.tolist()
    calibration['rightCameraMatrix'] = right_cm.tolist()

    # Distortion coefficients
    left_dc = [
        left_camera['intrinsics']['distortion']['radial']['k1'],
        left_camera['intrinsics']['distortion']['radial']['k2'],
        left_camera['intrinsics']['distortion']['radial']['k3'],
        left_camera['intrinsics']['distortion']['radial']['k4']
    ]
    right_dc = [
        right_camera['intrinsics']['distortion']['radial']['k1'],
        right_camera['intrinsics']['distortion']['radial']['k2'],
        right_camera['intrinsics']['distortion']['radial']['k3'],
        right_camera['intrinsics']['distortion']['radial']['k4']
    ]
    
    calibration['leftDistCoeffs'] = left_dc
    calibration['rightDistCoeffs'] = right_dc

    # Extrinsics (Rotation and Translation)
    R1 = np.array([
        [left_camera['extrinsics']['rotation']['r11'], left_camera['extrinsics']['rotation']['r12'], left_camera['extrinsics']['rotation']['r13']],
        [left_camera['extrinsics']['rotation']['r21'], left_camera['extrinsics']['rotation']['r22'], left_camera['extrinsics']['rotation']['r23']],
        [left_camera['extrinsics']['rotation']['r31'], left_camera['extrinsics']['rotation']['r32'], left_camera['extrinsics']['rotation']['r33']]
    ])
    R2 = np.array([
        [right_camera['extrinsics']['rotation']['r11'], right_camera['extrinsics']['rotation']['r12'], right_camera['extrinsics']['rotation']['r13']],
        [right_camera['extrinsics']['rotation']['r21'], right_camera['extrinsics']['rotation']['r22'], right_camera['extrinsics']['rotation']['r23']],
        [right_camera['extrinsics']['rotation']['r31'], right_camera['extrinsics']['rotation']['r32'], right_camera['extrinsics']['rotation']['r33']]
    ])

    calibration['R1'] = R1.tolist()
    calibration['R2'] = R2.tolist()

    # Calculate baseline
    T1 = np.array([
        left_camera['extrinsics']['translation']['tx'],
        left_camera['extrinsics']['translation']['ty'],
        left_camera['extrinsics']['translation']['tz']
    ])
    T2 = np.array([
        right_camera['extrinsics']['translation']['tx'],
        right_camera['extrinsics']['translation']['ty'],
        right_camera['extrinsics']['translation']['tz']
    ])
    
    baseline = np.linalg.norm(T2 - T1)
    calibration['baseline'] = baseline

    # Image width and height
    calibration['imageWidth'] = width
    calibration['imageHeight'] = height

    return calibration

def main():
    parser = argparse.ArgumentParser(description='Parse and convert calibration data.')
    parser.add_argument('input_file', help='Input calibration file in JSON format')
    parser.add_argument('--width', default=512, help='Width of calibration image')
    parser.add_argument('--height', default=512, help='Height of calibration image')
    parser.add_argument('-o', '--output_file', help='Output calibration file in JSON format')

    args = parser.parse_args()
    input_file = args.input_file

    calibration_data = parse_calibration(input_file, args.width, args.height)

    if args.output_file:
        output_file = args.output_file
        with open(output_file, 'w') as f:
            json.dump(calibration_data, f, indent=4)
    else:
        print(json.dumps(calibration_data, indent=4))

if __name__ == '__main__':
    main()
