import os


class Service:
    @staticmethod
    def get_filenames_mars_img() -> list[str]:
        return os.listdir('static/images/mars_image')
