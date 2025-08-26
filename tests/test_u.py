from __future__ import annotations

import io
import unittest

from PIL import Image

import piexif
from piexif import (
    InvalidImageDataError,
    _common,
    helper,
)

from .utils import INPUT_FILE1, NOAPP01_FILE, I1


class UTests(unittest.TestCase):
    def test_ExifReader_return_unknown(self):
        b1 = b"MM\x00\x2a\x00\x00\x00\x08"
        b2 = b"\x00\x01" + b"\xff\xff\x00\x00\x00\x00" + b"\x00\x00\x00\x00"
        er = piexif._load._ExifReader(b1 + b2)
        if er.tiftag[0:2] == b"II":
            er.endian_mark = "<"
        else:
            er.endian_mark = ">"
        ifd = er.get_ifd_dict(8, "0th", True)
        self.assertEqual(ifd[65535][0], 0)
        self.assertEqual(ifd[65535][1], 0)
        self.assertEqual(ifd[65535][2], b"\x00\x00")

    def test_ExifReader_convert_value_fail(self):
        er = piexif._load._ExifReader(I1)
        with self.assertRaises(ValueError):
            er.convert_value((None, None, None, None))

    def test_split_into_segments_fail1(self):
        with self.assertRaises(InvalidImageDataError):
            _common.split_into_segments(b"I'm not JPEG")

    def test_split_into_segments_fail2(self):
        with self.assertRaises(ValueError):
            _common.split_into_segments(b"\xff\xd8\xff\xe1\xff\xff")

    def test_merge_segments(self):
        # Remove APP0, when both APP0 and APP1 exists.
        with open(INPUT_FILE1, "rb") as f:
            original = f.read()
        segments = _common.split_into_segments(original)
        new_data = _common.merge_segments(segments)
        segments = _common.split_into_segments(new_data)
        self.assertFalse(
            segments[1][0:2] == b"\xff\xe0" and segments[2][0:2] == b"\xff\xe1"
        )
        self.assertEqual(segments[1][0:2], b"\xff\xe1")
        o = io.BytesIO(new_data)
        without_app0 = o.getvalue()
        Image.open(o).close()

        exif = _common.get_exif_seg(segments)

        # Remove Exif, when second 'merged_segments' arguments is None
        # and no APP0.
        segments = _common.split_into_segments(without_app0)
        new_data = _common.merge_segments(segments, None)
        segments = _common.split_into_segments(new_data)
        self.assertNotEqual(segments[1][0:2], b"\xff\xe0")
        self.assertNotEqual(segments[1][0:2], b"\xff\xe1")
        self.assertNotEqual(segments[2][0:2], b"\xff\xe1")
        o = io.BytesIO(new_data)
        Image.open(o).close()

        # Insert exif to jpeg that has APP0 and Exif.
        o = io.BytesIO()
        i = Image.new("RGB", (8, 8))
        i.save(o, format="jpeg", exif=exif)
        o.seek(0)
        segments = _common.split_into_segments(o.getvalue())
        new_data = _common.merge_segments(segments, exif)
        segments = _common.split_into_segments(new_data)
        self.assertFalse(
            segments[1][0:2] == b"\xff\xe0" and segments[2][0:2] == b"\xff\xe1"
        )
        self.assertEqual(segments[1], exif)
        o = io.BytesIO(new_data)
        Image.open(o).close()

        # Insert exif to jpeg that doesn't have APP0 and Exif.
        with open(NOAPP01_FILE, "rb") as f:
            original = f.read()
        segments = _common.split_into_segments(original)
        new_data = _common.merge_segments(segments, exif)
        segments = _common.split_into_segments(new_data)
        self.assertEqual(segments[1][0:2], b"\xff\xe1")
        o = io.BytesIO(new_data)
        Image.open(o).close()

        # Remove Exif, when second 'merged_segments' arguments is None
        # and Exif exists.
        with open(INPUT_FILE1, "rb") as f:
            original = f.read()
        segments = _common.split_into_segments(original)
        new_data = _common.merge_segments(segments, None)
        segments = _common.split_into_segments(new_data)
        self.assertNotEqual(segments[1][0:2], b"\xff\xe1")
        self.assertNotEqual(segments[2][0:2], b"\xff\xe1")
        o = io.BytesIO(new_data)
        Image.open(o).close()

    def test_dump_user_comment(self):
        # ascii
        header = b"\x41\x53\x43\x49\x49\x00\x00\x00"
        string = "abcd"
        binary = header + string.encode("ascii")
        result = helper.UserComment.dump(string, "ascii")
        self.assertEqual(binary, result)

        # jis
        header = b"\x4a\x49\x53\x00\x00\x00\x00\x00"
        string = "abcd"
        binary = header + string.encode("shift_jis")
        result = helper.UserComment.dump(string, "jis")
        self.assertEqual(binary, result)

        # unicode
        header = b"\x55\x4e\x49\x43\x4f\x44\x45\x00"
        string = "abcd"
        binary = header + string.encode("utf-16-be")
        result = helper.UserComment.dump(string, "unicode")
        self.assertEqual(binary, result)

        # undefined
        header = b"\x00\x00\x00\x00\x00\x00\x00\x00"
        string = "abcd"
        binary = header + string.encode("latin")
        self.assertRaises(ValueError, helper.UserComment.dump, string, "undefined")

    def test_load_user_comment(self):
        # ascii
        header = b"\x41\x53\x43\x49\x49\x00\x00\x00"
        string = "abcd"
        binary = header + string.encode("ascii")
        result = helper.UserComment.load(binary)
        self.assertEqual(string, result)

        # jis
        header = b"\x4a\x49\x53\x00\x00\x00\x00\x00"
        string = "abcd"
        binary = header + string.encode("shift_jis")
        result = helper.UserComment.load(binary)
        self.assertEqual(string, result)

        # unicode
        header = b"\x55\x4e\x49\x43\x4f\x44\x45\x00"
        string = "abcd"
        binary = header + string.encode("utf-16-be")
        result = helper.UserComment.load(binary)
        self.assertEqual(string, result)

        # undefined
        header = b"\x00\x00\x00\x00\x00\x00\x00\x00"
        string = "abcd"
        binary = header + string.encode("ascii")
        self.assertRaises(ValueError, helper.UserComment.load, binary)
