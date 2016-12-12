import os
import sys
import math
import pygame as pg
import client
import threading
from game import *

thread = threading.Thread(target=process)
thread.daemon = True
thread.start()

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.mouse.set_visible(False)
    Control(1).main_loop()
    pg.quit()
    sys.exit()
    
#INIT

main()
