# Importing Libraries
import os
import cv2
import threading
import time
import logging


path = os.path.dirname(os.path.realpath(__file__))


class Camera:

    def __init__(self, video_source=0, fps=20, max_frames=20):
        logging.info(f"Initializing camera source {video_source} with {fps} fps buffering {max_frames} frames")
        self.video_source = video_source
        self.max_frames = max_frames
        self.fps = 20
        self.fps_min = 1
        self.fps_max = 30
        self.set_fps(fps) 

        self.frames = []
        self.isrunning = False
        self.thread = None
        self.camera = None

        self.img_off = None
        with open(path + "/static/camera_off.jpg","rb") as imagefile:
             self.img_off = imagefile.read()

        self.img_black = None
        with open(path + "/static/camera_black.jpg","rb") as imagefile:
            self.img_black = imagefile.read()



    def __del__(self):
        self.stop()



    def start(self):
        logging.info("Starting ...")

        ok = True

        if self.camera is not None:
            logging.error("Camera in still open")
            ok = False

        if self.thread is not None:
            logging.error("Thread is still running")
            ok = False

        if ok:
            logging.debug("Opening camera")
            self.camera = cv2.VideoCapture(self.video_source)

            if self.camera.isOpened():
                logging.debug("Camera opened")
            else:
                logging.error("Camera can not be opened")
                self.camera = None
                ok = False

        if ok:
            logging.debug("Creating thread")
            self.thread = threading.Thread(target=self._capture, daemon=True)
            self.isrunning = True
            self.thread.start()
            logging.debug("Thread started")



    def stop(self):
        logging.info("Stopping ...")

        self.isrunning = False
        self.thread.join()
        self.thread = None
        logging.debug("Thread terminated")

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        logging.debug("Camera closed")



    def is_running(self):
        return self.isrunning



    def set_fps(self, fps):
        if fps >= self.fps_min and fps <= self.fps_max:
            self.fps = fps
        return self.fps



    def get_fps(self):
        return self.fps



    def get_image(self):
        if not self.isrunning:
            img = self.img_off
        elif len(self.frames) > 0:
            img = cv2.imencode('.jpg', self.frames[-1])[1].tobytes()
        else:
            img = self.img_black

        return img



    def generate_image(self):
        time_last = time.time()
        while True:
            #check if the output frame is available, otherwise skip
            if self.isrunning:
                time_tick = 1/self.fps
            else:
                time_tick = 1

            time_min = time_tick - (time.time() - time_last)
            
            if time_min > 0 and time_min < 1:
                time.sleep(time_min)

            image = self.get_image()

            # yield the output frame in the byte format
            time_last = time.time()
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(image) + b'\r\n')



    def _capture(self):
        logging.info("Capture loop started ... ")

        while self.isrunning:
            res, img = self.camera.read()
            if res:
                if len(self.frames)==self.max_frames:
                    self.frames = self.frames[1:]
                self.frames.append(img)
            time.sleep(1/self.fps)

        logging.info("Capture loop stopped ... ")


