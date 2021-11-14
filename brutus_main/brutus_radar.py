# Importing Libraries
import os
import cv2
import threading
import time
import logging
import math


path = os.path.dirname(os.path.realpath(__file__))


class Radar:

    MODE_SCAN = "scan"
    MODE_STATIC = "static"

    RAY_LENGTH = 80
    RAY_CENTER_X = 160
    RAY_CENTER_Y = 110


    def __init__(self, radar_device=None):
        logging.info(f"Initializing radar screen")

        self.isrunning = False
        self.thread = None

        self.img_off = None
        with open(path + "/static/radar_off.jpg","rb") as imagefile:
             self.img_off = imagefile.read()

        self.screen_lock = threading.Lock()
        self.screen_img = cv2.imread(path + "/static/radar_background.jpg")


        self.radar = radar_device
        self.radar.msg_table_register_func("pos", self.update_screen)

        self.set_range( -60, 60)
        self.set_pos( 0 )
        self.set_mode( self.MODE_SCAN )

        
        self.ray_table = []
        for i in range (25):
            angle = i * 5 - 60
            angle = (2 * math.pi) * (angle / 360)
            self.ray_table.append( 
                ( 
                    ( self.RAY_CENTER_X, self.RAY_CENTER_Y ), 
                    ( int(self.RAY_CENTER_X + self.RAY_LENGTH * math.sin(angle) + 0.5), int(self.RAY_CENTER_Y - self.RAY_LENGTH * math.cos(angle) + 0.5) )
                ) 
            )

    def __del__(self):
        self.stop()

    def start(self):
        logging.info("Starting ...")
        self.radar.command("start")
        self.isrunning = True

    def stop(self):
        logging.info("Stopping ...")
        self.radar.command("stop")
        self.isrunning = False

    def is_running(self):
        return self.isrunning

    def set_range(self, range_from, range_to):
        self.range_from = range_from
        self.range_to = range_to

    def get_range(self):
        return self.range_from, self.range_to

    def set_pos(self, pos):
        self.static_pos = pos

    def get_pos(self):
        return self.static_pos

    def set_mode(self, mode):
        if mode in [self.MODE_SCAN, self.MODE_STATIC]:
            self.mode = mode
            if mode  == self.MODE_SCAN:
                self.radar.command("range", self.range_from, self.range_to)
            elif mode == self.MODE_STATIC:
                self.radar.command("pos", self.static_pos)

    def get_mode(self):
        return self.mode

    def clear_screen(self):
        with self.screen_lock:
            self.screen_img = cv2.imread(path + "/static/radar_background.jpg")

    def update_screen(self, pos, distance ):
        if not self.isrunning:
            return
        else:
            with self.screen_lock:
                pos = int(pos)
                distance = int(self.RAY_LENGTH * int(distance) / 200)

                if distance < 0:
                    distance = 0
                elif distance > self.RAY_LENGTH:
                    distance = self.RAY_LENGTH

                i = int(12 - pos / 5)
                pos_0 = self.ray_table[i][0]
                pos_1 = self.ray_table[i][1]

                pos_d_x = pos_0[0] - int((pos_0[0] - pos_1[0]) * distance / self.RAY_LENGTH)
                pos_d_y = pos_0[1] - int((pos_0[1] - pos_1[1]) * distance / self.RAY_LENGTH)
                pos_d = (pos_d_x, pos_d_y)

                # draw black line to erase the old lines
                self.screen_img = cv2.line(self.screen_img, pos_0, pos_1, (0,0,0), 4)
                # draw the red line
                self.screen_img = cv2.line(self.screen_img, pos_d, pos_1, (0,0,255), 4)
                # draw the green line
                self.screen_img = cv2.line(self.screen_img, pos_0, pos_d, (0,255,0), 4)


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


