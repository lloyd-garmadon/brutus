# Importing Libraries
import os
import cv2
import threading
import time
import logging
import math


path = os.path.dirname(os.path.realpath(__file__))


class Sysinfo:

    def __init__(self):
        logging.info(f"Initializing system info")

        self.img_background = cv2.imread(path + "/static/sysinfo_background.jpg")

        # import psutil
        # # gives a single float value
        # psutil.cpu_percent()
        # # gives an object with many fields
        # psutil.virtual_memory()
        # # you can convert that object to a dictionary 
        # dict(psutil.virtual_memory()._asdict())
        # # you can have the percentage of used RAM
        # psutil.virtual_memory().percent
        # 79.2
        # # you can calculate percentage of available memory
        # psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
        # 20.8
        # psutil.sensors_temperatures()


    def get_image(self):
        img_scratch = self.img_background.copy()

        _, img = cv2.imencode(".jpg", img_scratch)

        return img


    def generate_image(self):
        time_last = time.time()
        while True:
            time_tick = 0.1
            
            time_min = time_tick - (time.time() - time_last)
            
            if time_min > 0 and time_min < 1:
                time.sleep(time_min)

            image = self.get_image()

            time_last = time.time()

            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(image) + b'\r\n')
