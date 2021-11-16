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
        self.device.command("q")
        
    def __del__(self):
        self.stop()

    def forward(self):
        self.device.command("w")

    def backward(self):
        self.device.command("s")

    def left(self):
        self.device.command("a")

    def right(self):
        self.device.command("d")

    def stop(self):
        self.device.command("q")

    def center(self):
        self.device.command("e")

