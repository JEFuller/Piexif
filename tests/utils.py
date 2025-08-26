# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import struct

from PIL import Image

import piexif
from piexif import (
    GPSIFD,
    ExifIFD,
    ImageIFD,
)

IMAGE_DIR = "tests/images/"
OUT_DIR = "tests/images/out/"

INPUT_FILE1 = os.path.join("tests", "images", "01.jpg")
INPUT_FILE2 = os.path.join("tests", "images", "02.jpg")
INPUT_FILE_PEN = os.path.join("tests", "images", "r_pen.jpg")
NOEXIF_FILE = os.path.join("tests", "images", "noexif.jpg")
# JPEG without APP0 and APP1 segments
NOAPP01_FILE = os.path.join("tests", "images", "noapp01.jpg")
INPUT_FILE_TIF = os.path.join("tests", "images", "01.tif")


with open(INPUT_FILE1, "rb") as f:
    I1 = f.read()
with open(INPUT_FILE2, "rb") as f:
    I2 = f.read()

ZEROTH_IFD = {
    ImageIFD.Software: b"PIL",  # ascii
    ImageIFD.Make: b"Make",  # ascii
    ImageIFD.Model: b"XXX-XXX",  # ascii
    ImageIFD.ResolutionUnit: 65535,  # short
    ImageIFD.BitsPerSample: (24, 24, 24),  # short * 3
    ImageIFD.XResolution: (4294967295, 1),  # rational
    ImageIFD.BlackLevelDeltaH: ((1, 1), (1, 1), (1, 1)),  # srational
    ImageIFD.ZZZTestSlong1: -11,
    ImageIFD.ZZZTestSlong2: (-11, -11, -11, -11),
}


EXIF_IFD = {
    ExifIFD.DateTimeOriginal: b"2099:09:29 10:10:10",  # ascii
    ExifIFD.LensMake: b"LensMake",  # ascii
    ExifIFD.OECF: b"\xaa\xaa\xaa\xaa\xaa\xaa",  # undefined
    ExifIFD.Sharpness: 65535,  # short
    ExifIFD.ISOSpeed: 4294967295,  # long
    ExifIFD.ExposureTime: (4294967295, 1),  # rational
    ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
    ExifIFD.ExposureBiasValue: (2147483647, -2147483648),  # srational
}


GPS_IFD = {
    GPSIFD.GPSVersionID: (0, 0, 0, 1),  # byte
    GPSIFD.GPSAltitudeRef: 1,  # byte
    GPSIFD.GPSDateStamp: b"1999:99:99 99:99:99",  # ascii
    GPSIFD.GPSDifferential: 65535,  # short
    GPSIFD.GPSLatitude: (4294967295, 1),  # rational
}


FIRST_IFD = {
    ImageIFD.Software: b"PIL",  # ascii
    ImageIFD.Make: b"Make",  # ascii
    ImageIFD.Model: b"XXX-XXX",  # ascii
    ImageIFD.BitsPerSample: (24, 24, 24),  # short * 3
    ImageIFD.BlackLevelDeltaH: ((1, 1), (1, 1), (1, 1)),  # srational
}


INTEROP_IFD = {piexif.InteropIFD.InteroperabilityIndex: b"R98"}


def iter_pil_compatible_images(filenames: list[str]) -> str:
    for filename in filenames:
        Image.open(IMAGE_DIR + filename)
        yield filename


def load_exif_by_PIL(f):
    i = Image.open(f)
    e = i._getexif()
    i.close()
    return e


def pack_byte(*args):
    return struct.pack("B" * len(args), *args)
