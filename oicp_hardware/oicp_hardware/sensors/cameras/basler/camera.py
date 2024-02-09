
from pypylon import pylon
import os
import numpy as np
import cv2
from uuid import uuid4

os.environ["PYLON_CAMEMU"] = "1"

class Basler:
    def init_controller(self):
        self.cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    def init_dector(self, controller=None):
        self.cam.Open()

    def commit_settings(self, param):
        pass

    def grab_data(self, naverage):
        result = self.cam.GrabOne(100)
        print("Mean Gray value:", np.mean(result.Array[0:20, 0]))
        cv2.imwrite(f'test_{uuid4().hex}.png', result.Array)
        return result.Array

    def stop(self):
        self.cam.Close()

    def callback(self, array):
        pass
    