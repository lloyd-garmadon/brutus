# Importing Libraries
import os
import cv2
import threading
import time
import logging
import math


path = os.path.dirname(os.path.realpath(__file__))


class Drive:

    def __init__(self, device=None):
        logging.info(f"Initializing drive controller")

        self.device = device
        self.device.command("stop")
        
    def __del__(self):
        self.stop()

    def forward(self):
        self.device.command("forward")

    def backward(self):
        self.device.command("backward")

    def left(self):
        self.device.command("left")

    def right(self):
        self.device.command("right")

    def stop(self):
        self.device.command("stop")

    def center(self):
        self.device.command("center")

