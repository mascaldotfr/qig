import argparse
import os

MINPIXELS = 0
MAXIMAGES = 0

class ValidInt(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        if value <= 0:
             parser.error(f"'{option_string}' must be positive !")
        elif value > 100000  and option_string in ("-n", "--number"):
             parser.error(f"'{option_string}' should be in the 1-{MAXIMAGES} range !")
        setattr(namespace, self.dest, value)

class MinimalPixels(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        if value != "random":
            for val in value.split("x"):
                if not val.isdigit():
                    parser.error(f"'{option_string}' should be in the 'WxH' format !")
                    return
                if int(val) < MINPIXELS :
                     parser.error(f"'{option_string}' must be > {MINPIXELS}")
        setattr(namespace, self.dest, value)

class ArgumentParser():
    def __init__(self, minpixels, maximages, img_formats):
        global MINPIXELS, MAXIMAGES
        MINPIXELS = minpixels
        MAXIMAGES = maximages
        ncpus = os.cpu_count()

        parser = argparse.ArgumentParser(prog="qig", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-f", "--format", required=True, choices=img_formats,
                            help="Image formats to generate")
        parser.add_argument("-n", "--number", required=True, type=int, action=ValidInt,
                            help=f"Number of images to generate (Range: 1-{MAXIMAGES})")
        parser.add_argument("-r", "--resolution", required=True,
                            help=f"Resolution in 'WxH' format, > {MINPIXELS}px, or 'random' for random dimensions",
                            action=MinimalPixels)
        parser.add_argument("-w", "--workers", type=int, action=ValidInt, default=ncpus,
                            help="Number of workers used")
        parser.add_argument("DIRECTORY", help="Target directory")
        self.args = parser.parse_args()

