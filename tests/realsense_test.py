import time
import cv2
from src.CameraHandler.RealSenseHandler import RealSenseHandler

if __name__ == '__main__':
    print('Connecting RS...')
    rs_camera = RealSenseHandler('./configs/rsd435.json')
    print(f'Connected!')
    
    try:
        time_start = time.time()
        while True:
            color, depth = rs_camera.get_color_and_depth()
            print(f'fps: {1 / (time.time() - time_start)}')
            time_start = time.time()
            color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
            cv2.imshow("h",color)
            cv2.waitKey(1)
    finally:
        cv2.destroyAllWindows()