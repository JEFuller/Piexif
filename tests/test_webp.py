from __future__ import annotations

import logging
import os
import unittest

from PIL import Image

import piexif
from piexif import _webp


from .utils import IMAGE_DIR, OUT_DIR, iter_pil_compatible_images


class WebpTests(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(OUT_DIR):
            os.mkdir(OUT_DIR)

    def test_merge_chunks(self):
        """Can PIL open our output WebP?"""
        files = [
            "tool1.webp",
            "pil1.webp",
            "pil2.webp",
            "pil3.webp",
            "pil_rgb.webp",
            "pil_rgba.webp",
        ]

        for filename in iter_pil_compatible_images(files):
            with open(IMAGE_DIR + filename, "rb") as f:
                data = f.read()

            chunks = _webp.split(data)
            file_header = _webp.get_file_header(chunks)
            merged = _webp.merge_chunks(chunks)
            new_webp_bytes = file_header + merged
            with open(OUT_DIR + "raw_" + filename, "wb") as f:
                f.write(new_webp_bytes)
            Image.open(OUT_DIR + "raw_" + filename)

    def test_insert_exif(self):
        """Can PIL open WebP that is inserted exif?"""
        files = [
            "tool1.webp",
            "pil1.webp",
            "pil2.webp",
            "pil3.webp",
            "pil_rgb.webp",
            "pil_rgba.webp",
        ]

        exif_dict = {
            "0th": {
                piexif.ImageIFD.Software: b"PIL",
                piexif.ImageIFD.Make: b"Make",
            }
        }

        for filename in iter_pil_compatible_images(files):
            with open(IMAGE_DIR + filename, "rb") as f:
                data = f.read()
            exif_bytes = piexif.dump(exif_dict)
            exif_inserted = _webp.insert(data, exif_bytes)
            with open(OUT_DIR + "i_" + filename, "wb") as f:
                f.write(exif_inserted)
            Image.open(OUT_DIR + "i_" + filename)

    def test_remove_exif(self):
        """Can PIL open WebP that is removed exif?"""
        files = [
            "tool1.webp",
            "pil1.webp",
            "pil2.webp",
            "pil3.webp",
            "pil_rgb.webp",
            "pil_rgba.webp",
        ]

        for filename in iter_pil_compatible_images(files):
            with open(IMAGE_DIR + filename, "rb") as f:
                data = f.read()
            exif_removed = _webp.remove(data)
            with open(OUT_DIR + "r_" + filename, "wb") as f:
                f.write(exif_removed)
            Image.open(OUT_DIR + "r_" + filename)

    def test_get_exif(self):
        """Can we get exif from WebP?"""
        files = [
            "tool1.webp",
        ]

        for filename in iter_pil_compatible_images(files):
            with open(IMAGE_DIR + filename, "rb") as f:
                data = f.read()
            exif_bytes = _webp.get_exif(data)
            self.assertEqual(exif_bytes[0:2], b"MM")

    def test_load(self):
        """Can we get exif from WebP?"""
        files = [
            "tool1.webp",
        ]

        for filename in iter_pil_compatible_images(files):
            logging.info(piexif.load(IMAGE_DIR + filename))

    def test_remove(self):
        """Can PIL open WebP that is removed exif?"""
        files = [
            "tool1.webp",
            "pil1.webp",
            "pil2.webp",
            "pil3.webp",
            "pil_rgb.webp",
            "pil_rgba.webp",
        ]

        for filename in iter_pil_compatible_images(files):
            Image.open(IMAGE_DIR + filename)
            piexif.remove(IMAGE_DIR + filename, OUT_DIR + "rr_" + filename)
            Image.open(OUT_DIR + "rr_" + filename)

    def test_insert(self):
        """Can PIL open WebP that is inserted exif?"""
        files = [
            "tool1.webp",
            "pil1.webp",
            "pil2.webp",
            "pil3.webp",
            "pil_rgb.webp",
            "pil_rgba.webp",
        ]

        exif_dict = {
            "0th": {
                piexif.ImageIFD.Software: b"PIL",
                piexif.ImageIFD.Make: b"Make",
            }
        }
        exif_bytes = piexif.dump(exif_dict)

        for filename in files:
            try:
                Image.open(IMAGE_DIR + filename)
            except Exception:
                print("Pillow can't read {}".format(filename))
                continue
            piexif.insert(exif_bytes, IMAGE_DIR + filename, OUT_DIR + "ii_" + filename)
            Image.open(OUT_DIR + "ii_" + filename)
