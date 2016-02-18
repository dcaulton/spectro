import os
import sys

import picamera


class Picam(object):
    '''
    Handles taking pictures with with the Picam (ambient light) camera via the software bindings from the picamera package
    '''

    def __init__(self):
        self.root_directory = '/home/pi/Pictures' #TODO move this into settings.py:IMAGE_SAVE_PATH

    def take_still(self, pic_name, image_width=1200, image_height=900):
        with picamera.PiCamera() as camera:
            camera.resolution = (image_width, image_height)
            pic_path = os.path.join(self.root_directory, pic_name)
            camera.capture(pic_path)
            return pic_path

if __name__ == '__main__':
    camera = Picam()
    if len(sys.argv) > 1:
        pic_name = sys.argv
    else:
        pic_name = 'out.jpg'
    camera.take_still(pic_name)
