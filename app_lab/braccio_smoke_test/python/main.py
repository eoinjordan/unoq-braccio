from arduino.app_utils import App
import time


def loop():
    time.sleep(1)


App.run(user_loop=loop)
