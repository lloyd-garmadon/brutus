# Importing Libraries
import os
import cv2
import threading
import time
import logging
import math


path = os.path.dirname(os.path.realpath(__file__))


class Drive:

    FONT_COLOR     = (0,0,255)

    POINTER_POS     = (70,80)
    POINTER_LENGTH  = 55
    POINTER_COLOR   = (0,255,0)

    SPEED_CURR_POS = (75,116)
    SPEED_CURR_FONT_SCALE = 0.9
    SPEED_CURR_FONT_THICKNESS = 2
    SPEED_CURR_FONT_LINETYPE  = 2

    SPEED_CURR_L_POS = (10,170)
    SPEED_CURR_R_POS = (80,170)
    SPEED_CURR_X_FONT_SCALE = 0.45
    SPEED_CURR_X_FONT_THICKNESS = 2
    SPEED_CURR_X_FONT_LINETYPE  = 2


    SPEED_CTRL_L_POS = (10,183)
    SPEED_CTRL_R_POS = (80,183)
    SPEED_CTRL_X_FONT_SCALE = 0.3
    SPEED_CTRL_X_FONT_THICKNESS = 2
    SPEED_CTRL_X_FONT_LINETYPE  = 2

    def __init__(self, device=None):
        logging.info(f"Initializing drive controller")

        self.img_background = cv2.imread(path + "/static/drive_background.jpg")

        self.speed_ctrl_l = 0
        self.speed_ctrl_r = 0
        self.speed_curr_l = 0
        self.speed_curr_r = 0
        self.speed_curr = 0

        self.device = device
        self.device.cmd_table_assign_func("q", self.cmd_respond)
        self.device.cmd_table_assign_func("e", self.cmd_respond)
        self.device.cmd_table_assign_func("w", self.cmd_respond)
        self.device.cmd_table_assign_func("s", self.cmd_respond)
        self.device.cmd_table_assign_func("a", self.cmd_respond)
        self.device.cmd_table_assign_func("d", self.cmd_respond)
        self.device.msg_table_register_func("speed", self.msg_respond)
        self.device.command("q", wait=False)


    def __del__(self):
        self.stop()

    def forward(self):
        self.device.command("w", wait=False)

    def backward(self):
        self.device.command("s", wait=False)

    def left(self):
        self.device.command("a", wait=False)

    def right(self):
        self.device.command("d", wait=False)

    def stop(self):
        self.device.command("q", wait=False)

    def center(self):
        self.device.command("e", wait=False)

    def center(self):
        self.device.command("e", wait=False)

    def cmd_respond(self, res, cmd_name, speed_l, speed_r):
        self.speed_ctrl_l = int(speed_l)
        self.speed_ctrl_r = int(speed_r)

    def msg_respond(self, speed_l, speed_r):
        self.speed_curr_l = int(speed_l)
        self.speed_curr_r = int(speed_r)
        self.speed_curr = int((speed_l + speed_r) / 2)


    def get_image(self):
        img_scratch = self.img_background.copy()

        speed = self.speed_curr if (self.speed_curr > 0) else -self.speed_curr
        angle = 180 * speed / 100 - 135
        angle = 2 * math.pi * angle / 360
        pos_0 = self.POINTER_POS
        pos_1 = ( math.cos(angle), math.sin(angle) )
        pos_1 = ( pos_1[0] * self.POINTER_LENGTH, pos_1[1] * self.POINTER_LENGTH )
        pos_1 = ( pos_0[0] + pos_1[0], pos_0[1] - pos_1[1] )
        pos_1 = ( int(pos_1[0]), int(pos_1[1]) )
        cv2.line(img_scratch,    pos_0, pos_1,  self.POINTER_COLOR, 4)
        cv2.putText(img_scratch, str( speed ),  self.SPEED_CURR_POS,   cv2.FONT_HERSHEY_SIMPLEX, self.SPEED_CURR_FONT_SCALE,   self.FONT_COLOR, self.SPEED_CURR_FONT_THICKNESS,   self.SPEED_CURR_FONT_LINETYPE )

        cv2.putText(img_scratch, str(self.speed_curr_l), self.SPEED_CURR_L_POS, cv2.FONT_HERSHEY_SIMPLEX, self.SPEED_CURR_X_FONT_SCALE, self.FONT_COLOR, self.SPEED_CURR_X_FONT_THICKNESS, self.SPEED_CURR_X_FONT_LINETYPE )
        cv2.putText(img_scratch, str(self.speed_curr_r), self.SPEED_CURR_R_POS, cv2.FONT_HERSHEY_SIMPLEX, self.SPEED_CURR_X_FONT_SCALE, self.FONT_COLOR, self.SPEED_CURR_X_FONT_THICKNESS, self.SPEED_CURR_X_FONT_LINETYPE )
        cv2.putText(img_scratch, str(self.speed_ctrl_l), self.SPEED_CTRL_L_POS, cv2.FONT_HERSHEY_SIMPLEX, self.SPEED_CTRL_X_FONT_SCALE, self.FONT_COLOR, self.SPEED_CTRL_X_FONT_THICKNESS, self.SPEED_CTRL_X_FONT_LINETYPE )
        cv2.putText(img_scratch, str(self.speed_ctrl_r), self.SPEED_CTRL_R_POS, cv2.FONT_HERSHEY_SIMPLEX, self.SPEED_CTRL_X_FONT_SCALE, self.FONT_COLOR, self.SPEED_CTRL_X_FONT_THICKNESS, self.SPEED_CTRL_X_FONT_LINETYPE )

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
