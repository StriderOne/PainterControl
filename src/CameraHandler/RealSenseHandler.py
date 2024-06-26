import numpy as np
import pyrealsense2 as rs
from typing import Tuple
import json
import os
import cv2
import time
import argparse


class RealSenseHandler():
    """A wrapper for pyrealsense
    Methods
    -------
    get_color_and_depth(void)
        Gets tuple[np.ndarray, np.ndarray] color and depth

    get_calibration(void)
        Gets tuple ([width, height, fx, fy, ppx, ppy], [distortion_coeffs])
    """


    def __init__(self, cfg_path: str = "rsd435.json") -> None:
        """
        Parameters
        ----------
            cfg_path (str, optional): String to config path. Defaults to 'cfg.json'.
        """
        try:
            with open(cfg_path) as f:
                cfg = json.load(f)
            print('pre pipeline')
            self._pipeline = rs.pipeline()
            print('pipeline')
            config = rs.config()
            print('rs config')
            self.width, self.height = cfg["color_w"], cfg["color_h"]
            config.enable_stream(
                rs.stream.color, cfg["color_w"], cfg["color_h"], rs.format.rgb8, cfg["fps"]
                )  # rs.format.rgb8
            print('rs stream')
            time.sleep(1)
            # config.enable_device(cfg['serial'])
            print('Enabled device by serial')
            # profile = config.resolve(pipeline)
            profile = self._pipeline.start(config)
            print('Resolved config')
            
            color_sensor = profile.get_device().first_color_sensor()
            print('color_sensor')
            profile_color = profile.get_stream(rs.stream.color) # Fetch stream profile for depth stream
            intr = profile_color.as_video_stream_profile().get_intrinsics() # Downcast to video_stream_profile and fetch intrinsics
            self._intrinsic = [
                intr.width,
                intr.height,
                intr.fx,
                intr.fy,
                intr.ppx,
                intr.ppy
            ]
            self._distortion = intr.coeffs       
            self._pcd = rs.pointcloud()
            print('set all options')
            
            self._save_pictures = cfg['save_pictures']
            self._verbose = cfg['verbose']
            if self._save_pictures:
                self._counter = 0
                os.makedirs('tmp/camera', exist_ok=True)
        except Exception as e:
            print(f'RealSenseHandler: INIT ERROR!\n    {e}')
            quit()
            
            
    def get_color_and_depth(self) -> Tuple[np.ndarray, np.ndarray]:
        """Gets depth and color frames from RealSense

        Returns
        -------
            tuple[np.array, np.array]
                Color and depth frames
        """
        time_start = time.time()
        try:
            frames = self._pipeline.wait_for_frames()
        except Exception:
            print("RealSenseHandler: Сan not get frames!")
            exit(0)
        color = np.asarray(frames.get_color_frame().get_data()).astype(np.uint8)
        depth = color
        if self._save_pictures:
            cv2.imwrite(f'tmp/camera/{self._counter}_color.jpg', color)
            cv2.imwrite(f'tmp/camera/{self._counter}_depth.jpg', depth)
            self._counter += 1
        if self._verbose:
            print(f"RealSenseHandler: Took {time.time() - time_start : .3} s")
            
        return (color, depth)


    def get_calibration(self) -> Tuple[list, list]:
        """Intrinsics and distortion getter

        Returns
        -------
            list
                width, height, fx, fy, ppx, ppy
            list  
                distortion coeffs
        """
        return self._intrinsic, self._distortion


    def get_pcd(self, depth_frame):
        points = self._pcd.calculate(depth_frame).get_vertices()
        verts = np.asanyarray(points).view(np.float32).reshape(-1, 3)
        return verts


if __name__ == '__main__':
    print('Connecting RS...')
    rs_camera = RealSenseHandler('rsd435.json')
    print(f'Connected!')
    
    time_start = time.time()
    while True:
        color, depth = rs_camera.get_color_and_depth()
        print(f'fps: {1 / (time.time() - time_start)}')
        time_start = time.time()
        color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
        cv2.imshow("h",color)
        cv2.waitKey(1)
    cv2.destroyAllWindows()