import struct
import unittest

import piexif


class TimeZoneOffsetTest(unittest.TestCase):
    def test_round_trip(self):
        tag = piexif.ImageIFD.TimeZoneOffset
        for offset in (-12, 0, 5, (-5, -4)):
            with self.subTest(offset=offset):
                encoded = piexif.dump({"0th": {tag: offset}})
                self.assertEqual(piexif.load(encoded)["0th"][tag], offset)

    def test_positive_offset_uses_signed_short(self):
        tag = piexif.ImageIFD.TimeZoneOffset
        encoded = piexif.dump({"0th": {tag: 5}})
        # The first IFD entry follows the Exif prefix, TIFF header and entry count.
        self.assertEqual(struct.unpack_from(">HHI", encoded, 16), (tag, 8, 1))
