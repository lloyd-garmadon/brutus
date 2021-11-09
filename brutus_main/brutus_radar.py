# Importing Libraries
import os
import cv2
import threading
import time
import logging


path = os.path.dirname(os.path.realpath(__file__))


class Radar:

    def __init__(self, radar_device=None):
        logging.info(f"Initializing radar screen")

        self.isrunning = False
        self.thread = None
        self.radar = None

        self.img_off = None
        with open(path + "/static/radar_off.jpg","rb") as imagefile:
             self.img_off = imagefile.read()

        self.screen_lock = threading.Lock()
        self.screen_img = cv2.imread(path + "/static/radar_background.jpg")


    def __del__(self):
        self.stop()


    def start(self):
        logging.info("Starting ...")
        self.isrunning = True


    def stop(self):
        logging.info("Stopping ...")
        self.isrunning = False


    def clear_screen(self):
        with self.screen_lock:
            self.screen_img = cv2.imread(path + "/static/radar_background.jpg")


    def is_running(self):
        return self.isrunning



    def get_image(self):
        if not self.isrunning:
            img = self.img_off
        else:
            with self.screen_lock:
                _, img = cv2.imencode(".jpg", self.screen_img)

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


