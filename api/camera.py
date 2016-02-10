import sys

import picamera


class Picam(object):
    '''
    Handles taking pictures with with the Picam (ambient light) camera via the software bindings from the picamera package
    '''

    def __init__(self):
        pass

    def take_still(self, pic_path, image_width=1200, image_height=900):
        with picamera.PiCamera() as camera:
            camera.resolution = (image_width, image_height)
            camera.capture(pic_path)

if __name__ == '__main__':
    camera = Picam()
    if len(sys.argv) > 1:
        pic_path = os.path.join('/home/pi/Pictures/', sys.argv)
    else:
        pic_path = '/home/pi/Pictures/out.jpg'
    camera.take_still(pic_path)
