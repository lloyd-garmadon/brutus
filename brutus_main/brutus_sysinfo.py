# Importing Libraries
import os
import cv2
import threading
import time
import logging
import math
import psutil


path = os.path.dirname(os.path.realpath(__file__))


class Sysinfo:

    FONT_SCALE     = 0.45
    FONT_COLOR     = (0,0,255)
    FONT_THICKNESS = 2
    FONT_LINETYPE  = 2

    BAR_LENGTH = 132
    BAR_HEIGHT = 10
    BAR_COLOR = (0,255,0)

    CPU_VALUE_POS = (68,25)
    CPU_BAR_POS   = (15,34)

    MEM_VALUE_POS = (75,91)
    MEM_BAR_POS   = (15,100)

    TEMP_VALUE_POS = (82,157)
    TEMP_BAR_POS   = (15,166)



    def __init__(self):
        logging.info(f"Initializing system info")

        self.img_background = cv2.imread(path + "/static/sysinfo_background.jpg")

        # gives a single float value

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
        # 


    def get_image(self):
        img_scratch = self.img_background.copy()

        cpu_usage = psutil.cpu_percent()
        cv2.putText(img_scratch, f"{cpu_usage:5.2f} %", self.CPU_VALUE_POS, cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE, self.FONT_COLOR, self.FONT_THICKNESS, self.FONT_LINETYPE )
        bar_start = self.CPU_BAR_POS
        bar_end = ( int(bar_start[0] + self.BAR_LENGTH * cpu_usage / 100), int(bar_start[1] + self.BAR_HEIGHT) )
        cv2.rectangle(img_scratch, bar_start, bar_end, self.BAR_COLOR, -1)

        mem_usage = 100 - psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
        cv2.putText(img_scratch, f"{mem_usage:5.2f} %", self.MEM_VALUE_POS, cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE, self.FONT_COLOR, self.FONT_THICKNESS, self.FONT_LINETYPE )
        bar_start = self.MEM_BAR_POS
        bar_end = ( int(bar_start[0] + self.BAR_LENGTH * mem_usage / 100), int(bar_start[1] + self.BAR_HEIGHT) )
        cv2.rectangle(img_scratch, bar_start, bar_end, self.BAR_COLOR, -1)

        temperature = psutil.sensors_temperatures()
        temperature = 36.7
        cv2.putText(img_scratch, f"{temperature:4.1f} °C", self.TEMP_VALUE_POS, cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE, self.FONT_COLOR, self.FONT_THICKNESS, self.FONT_LINETYPE )
        bar_start = self.TEMP_BAR_POS
        bar_end = ( int(bar_start[0] + self.BAR_LENGTH * temperature / 100), int(bar_start[1] + self.BAR_HEIGHT) )
        cv2.rectangle(img_scratch, bar_start, bar_end, self.BAR_COLOR, -1)

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
