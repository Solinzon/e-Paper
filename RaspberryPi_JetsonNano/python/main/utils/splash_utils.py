import os
import random

splash_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/image/splash')


class SplashUtils:

    def get_splash_pic_name(self) -> int:
        splash_num = 0
        for name in os.listdir(splash_dir):
            sub_path = os.path.join(splash_dir, name)
            print(sub_path)
            if os.path.isfile(sub_path) and "splash" in name:
                splash_num += 1

        return random.randint(0, splash_num)
