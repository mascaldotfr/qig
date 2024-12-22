#!/usr/bin/env python3

import concurrent.futures
import hashlib
import multiprocessing # pyinstaller
import random
import os

from PIL import Image, ImageDraw
import pillow_heif
from tqdm import tqdm

from lib.arguments import ArgumentParser

def generate_image(job, directory):
    mode = "RGBA" if job["format"] in ("png", "gif", "webp", "heic", "avif") else "RGB"
    image = Image.effect_noise((job["width"], job["height"]), random.uniform(1, 127))
    # Image is in grayscale by default, we need colors
    image = image.convert(mode)
    rrgba = random.sample(range(256), 4)
    rfactor = random.uniform(2, 16)
    eraser_size = (int(job["width"] / rfactor), int(job["height"] / rfactor))
    colortuple = rrgba if mode == "RGBA" else rrgba[:-1]
    eraser = Image.new(mode, eraser_size, tuple(colortuple))
    image.paste(eraser, (0, 0))
    imghash = hashlib.sha256(image.tobytes()).hexdigest()
    destination = os.path.join(directory, imghash + "." + job["format"])
    image.save(destination)

if __name__ == "__main__":
    multiprocessing.freeze_support() # pyinstaller
    pillow_heif.register_heif_opener()
    pillow_heif.register_avif_opener()
    # "random" should always be the last
    img_formats = ["jpeg", "jpg", "png", "gif", "webp", "heic", "heif", "avif",
                   "bmp", "pdf", "tiff", "random"]

    args = ArgumentParser(minpixels=32, maximages=100000, img_formats=img_formats).args
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        jobs = []
        for i in range(args.number):
            job = { }
            if args.format == "random":
                job["format"] = random.choice(img_formats[:-1])
            else:
                job["format"] = args.format
            if args.resolution == "random":
                job["width"], job["height"] = random.sample(range(32, 2560), 2)
            else:
               wh = args.resolution.split("x")
               job["width"] = int(wh[0])
               job["height"] = int(wh[1])
            jobs.append(job)
        jobs = tuple(jobs)

        futures = ( executor.submit(generate_image, job, args.DIRECTORY) for job in jobs )
        progress = tqdm(total=len(jobs))
        for result in concurrent.futures.as_completed(futures):
            progress.update(1)
            if result.exception() is not None:
                progress.close()
                executor.shutdown(wait=True)
                raise result.exception()
        progress.close()
        executor.shutdown(wait=True)

        print("Done.")

# vim: et ts=4 sw=4
