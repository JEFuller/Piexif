from __future__ import annotations

import glob
import io
import logging
import os
import struct
import time
import unittest

from PIL import Image
from PIL.TiffImagePlugin import IFDRational

import piexif
from piexif import (
    GPSIFD,
    TAGS,
    ExifIFD,
    ImageIFD,
)

from .utils import (
    INPUT_FILE1,
    INPUT_FILE2,
    INPUT_FILE_PEN,
    NOEXIF_FILE,
    INPUT_FILE_TIF,
    ZEROTH_IFD,
    EXIF_IFD,
    GPS_IFD,
    FIRST_IFD,
    INTEROP_IFD,
    load_exif_by_PIL,
    pack_byte,
    I1,
    I2,
)


class ExifTests(unittest.TestCase):
    """tests for main five functions."""

    # load ------
    def test_no_exif_load(self):
        exif_dict = piexif.load(NOEXIF_FILE)
        none_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "Interop": {},
            "1st": {},
            "thumbnail": None,
        }
        self.assertEqual(exif_dict, none_dict)

    def test_load_only(self):
        files = glob.glob(os.path.join("tests", "images", "r_*.jpg"))
        for input_file in files:
            exif = piexif.load(input_file)
            e = load_exif_by_PIL(input_file)
            self._compare_piexifDict_PILDict(exif, e)

    def test_load_m(self):
        """'load' on memory."""
        exif = piexif.load(I1)
        e = load_exif_by_PIL(INPUT_FILE1)
        logging.warning("********************\n\n%s\n", INPUT_FILE1)
        self._compare_piexifDict_PILDict(exif, e)

    def test_load_tif(self):
        exif = piexif.load(INPUT_FILE_TIF)
        zeroth_ifd = exif["0th"]
        exif_bytes = piexif.dump({"0th": zeroth_ifd})

        im = Image.new("RGB", (8, 8))
        o = io.BytesIO()
        im.save(o, format="jpeg", exif=exif_bytes)
        im.close()
        exif2 = piexif.load(o.getvalue())
        zeroth_ifd2 = exif2["0th"]
        self.assertDictEqual(zeroth_ifd, zeroth_ifd2)

    def test_load_tif_m(self):
        with open(INPUT_FILE_TIF, "rb") as f:
            tif = f.read()
        exif = piexif.load(tif)
        zeroth_ifd = exif["0th"]
        exif_bytes = piexif.dump({"0th": zeroth_ifd})

        im = Image.new("RGB", (8, 8))
        o = io.BytesIO()
        im.save(o, format="jpeg", exif=exif_bytes)
        im.close()
        exif2 = piexif.load(o.getvalue())
        zeroth_ifd2 = exif2["0th"]
        self.assertDictEqual(zeroth_ifd, zeroth_ifd2)

    def test_load_from_pilImage_property(self):
        o = io.BytesIO()
        i = Image.open(INPUT_FILE1)
        exif = i.info["exif"]
        exif_dict = piexif.load(exif)
        exif_bytes = piexif.dump(exif_dict)
        i.save(o, "jpeg", exif=exif_bytes)
        i.close()
        o.seek(0)
        Image.open(o).close()

    def test_load_name_dict(self):
        thumbnail_io = io.BytesIO()
        thumb = Image.open(INPUT_FILE2)
        thumb.thumbnail((40, 40))
        thumb.save(thumbnail_io, "JPEG")
        thumb.close()
        thumb_data = thumbnail_io.getvalue()
        exif_dict = {
            "0th": ZEROTH_IFD,
            "Exif": EXIF_IFD,
            "GPS": GPS_IFD,
            "Interop": INTEROP_IFD,
            "1st": FIRST_IFD,
            "thumbnail": thumb_data,
        }
        exif_bytes = piexif.dump(exif_dict)
        im = Image.new("RGB", (80, 80))

        o = io.BytesIO()
        im.save(o, format="jpeg", exif=exif_bytes)
        im.close()
        o.seek(0)
        exif = piexif.load(o.getvalue(), True)
        logging.warning(exif)

    def test_load_unicode_filename(self):
        input_file = os.path.join("tests", "images", "r_sony.jpg")
        exif = piexif.load(input_file)
        e = load_exif_by_PIL(input_file)
        self._compare_piexifDict_PILDict(exif, e)

    # dump ------
    def test_no_exif_dump(self):
        o = io.BytesIO()
        exif_bytes = piexif.dump({})
        i = Image.new("RGB", (8, 8))
        i.save(o, format="jpeg", exif=exif_bytes)
        o.seek(0)
        exif_dict2 = load_exif_by_PIL(o)
        self.assertDictEqual({}, exif_dict2)

    def test_dump(self):
        exif_dict = {"0th": ZEROTH_IFD, "Exif": EXIF_IFD, "GPS": GPS_IFD}
        t = time.time()
        exif_bytes = piexif.dump(exif_dict)
        t_cost = time.time() - t
        logging.debug("'dump': %s[sec]", t_cost)
        im = Image.new("RGB", (8, 8))

        o = io.BytesIO()
        im.save(o, format="jpeg", exif=exif_bytes)
        im.close()
        o.seek(0)
        load_exif_by_PIL(o)

    def test_dump_fail(self):
        with open(os.path.join("tests", "images", "large.jpg"), "rb") as f:
            thumb_data = f.read()
        exif_dict = {
            "0th": ZEROTH_IFD,
            "Exif": EXIF_IFD,
            "GPS": GPS_IFD,
            "Interop": INTEROP_IFD,
            "1st": FIRST_IFD,
            "thumbnail": thumb_data,
        }
        with self.assertRaises(ValueError):
            piexif.dump(exif_dict)

    def test_dump_fail2(self):
        exif_ifd = {ExifIFD.DateTimeOriginal: 123}
        exif_dict = {"Exif": exif_ifd}
        with self.assertRaises(ValueError):
            piexif.dump(exif_dict)

    def test_dump_fail3(self):
        exif_ifd = {ExifIFD.OECF: 1}
        exif_dict = {"Exif": exif_ifd}
        with self.assertRaises(ValueError):
            piexif.dump(exif_dict)

    def test_dump_fail4(self):
        exif_ifd = {ExifIFD.OECF: (1, 2, 3, 4, 5)}
        exif_dict = {"Exif": exif_ifd}
        with self.assertRaises(ValueError):
            piexif.dump(exif_dict)

    # load and dump ------
    def test_dump_and_load(self):
        exif_dict = {"0th": ZEROTH_IFD, "Exif": EXIF_IFD, "GPS": GPS_IFD}
        exif_bytes = piexif.dump(exif_dict)
        im = Image.new("RGB", (8, 8))

        o = io.BytesIO()
        im.save(o, format="jpeg", exif=exif_bytes)
        im.close()
        o.seek(0)
        exif = piexif.load(o.getvalue())
        zeroth_ifd, exif_ifd, gps_ifd = exif["0th"], exif["Exif"], exif["GPS"]
        zeroth_ifd.pop(ImageIFD.ExifTag)  # pointer to exif IFD
        zeroth_ifd.pop(ImageIFD.GPSTag)  # pointer to GPS IFD
        self.assertDictEqual(ZEROTH_IFD, zeroth_ifd)
        self.assertDictEqual(EXIF_IFD, exif_ifd)
        self.assertDictEqual(GPS_IFD, gps_ifd)

    def test_dump_and_load2(self):
        thumbnail_io = io.BytesIO()
        thumb = Image.open(INPUT_FILE2)
        thumb.thumbnail((40, 40))
        thumb.save(thumbnail_io, "JPEG")
        thumb.close()
        thumb_data = thumbnail_io.getvalue()
        exif_dict = {
            "0th": ZEROTH_IFD,
            "Exif": EXIF_IFD,
            "GPS": GPS_IFD,
            "Interop": INTEROP_IFD,
            "1st": FIRST_IFD,
            "thumbnail": thumb_data,
        }
        exif_bytes = piexif.dump(exif_dict)
        im = Image.new("RGB", (80, 80))

        o = io.BytesIO()
        im.save(o, format="jpeg", exif=exif_bytes)
        im.close()
        o.seek(0)
        exif = piexif.load(o.getvalue())
        exif["0th"].pop(ImageIFD.ExifTag)  # pointer to exif IFD
        exif["0th"].pop(ImageIFD.GPSTag)  # pointer to GPS IFD
        exif["Exif"].pop(ExifIFD.InteroperabilityTag)
        self.assertDictEqual(ZEROTH_IFD, exif["0th"])
        self.assertDictEqual(EXIF_IFD, exif["Exif"])
        self.assertDictEqual(GPS_IFD, exif["GPS"])
        self.assertDictEqual(INTEROP_IFD, exif["Interop"])
        exif["1st"].pop(513)  # pointer to exif IFD
        exif["1st"].pop(514)  # pointer to GPS IFD
        self.assertDictEqual(FIRST_IFD, exif["1st"])
        Image.open(io.BytesIO(exif["thumbnail"])).close()

    def test_dump_and_load3(self):
        ascii_v = ["a", "ab", "abc", "abcd", "abcde"]
        undefined_v = [
            b"\x00",
            b"\x00\x01",
            b"\x00\x01\x02",
            b"\x00\x01\x02\x03",
            b"\x00\x01\x02\x03\x04",
        ]
        byte_v = [
            255,
            (255, 254),
            (255, 254, 253),
            (255, 254, 253, 252),
            (255, 254, 253, 252, 251),
        ]
        short_v = [
            65535,
            (65535, 65534),
            (65535, 65534, 65533),
            (65535, 65534, 65533, 65532),
            (65535, 65534, 65533, 65532, 65531),
        ]
        long_v = [
            4294967295,
            (4294967295, 4294967294),
            (4294967295, 4294967294, 4294967293),
            (4294967295, 4294967294, 4294967293, 4294967292),
            (5, 4, 3, 2, 1),
        ]
        rational_v = [
            (4294967295, 4294967294),
            ((4294967295, 4294967294), (4294967293, 4294967292)),
            ((1, 2), (3, 4), (5, 6)),
            ((1, 2), (3, 4), (5, 6), (7, 8)),
            ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10)),
        ]
        srational_v = [
            (2147483647, -2147483648),
            ((2147483647, -2147483648), (2147483645, 2147483644)),
            ((1, 2), (3, 4), (5, 6)),
            ((1, 2), (3, 4), (5, 6), (7, 8)),
            ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10)),
        ]
        for x in range(5):
            exif_dict = {
                "0th": {
                    ImageIFD.ProcessingSoftware: ascii_v[x],
                    ImageIFD.InterColorProfile: undefined_v[x],
                    ImageIFD.SubfileType: short_v[x],
                    ImageIFD.WhitePoint: rational_v[x],
                    ImageIFD.BlackLevelDeltaH: srational_v[x],
                },
                "Exif": {ExifIFD.ISOSpeed: long_v[x]},
                "GPS": {GPSIFD.GPSVersionID: byte_v[x]},
            }
            exif_bytes = piexif.dump(exif_dict)
            e = piexif.load(exif_bytes)
            self.assertEqual(
                e["0th"][ImageIFD.ProcessingSoftware].decode("latin1"), ascii_v[x]
            )
            self.assertEqual(e["0th"][ImageIFD.InterColorProfile], undefined_v[x])
            self.assertEqual(e["0th"][ImageIFD.SubfileType], short_v[x])
            self.assertEqual(e["0th"][ImageIFD.WhitePoint], rational_v[x])
            self.assertEqual(e["0th"][ImageIFD.BlackLevelDeltaH], srational_v[x])
            self.assertEqual(e["Exif"][ExifIFD.ISOSpeed], long_v[x])
            self.assertEqual(e["GPS"][GPSIFD.GPSVersionID], byte_v[x])

    def test_dump_and_load_specials(self):
        """test dump and load special types(SingedByte, SiginedShort, DoubleFloat)"""
        zeroth_ifd_original = {
            ImageIFD.ZZZTestSByte: -128,
            ImageIFD.ZZZTestSShort: -32768,
            ImageIFD.ZZZTestDFloat: 1.0e-100,
        }
        exif_dict = {"0th": zeroth_ifd_original}
        exif_bytes = piexif.dump(exif_dict)

        exif = piexif.load(exif_bytes)
        zeroth_ifd = exif["0th"]
        self.assertEqual(
            zeroth_ifd_original[ImageIFD.ZZZTestSByte],
            zeroth_ifd[ImageIFD.ZZZTestSByte],
        )
        self.assertEqual(
            zeroth_ifd_original[ImageIFD.ZZZTestSShort],
            zeroth_ifd[ImageIFD.ZZZTestSShort],
        )
        self.assertEqual(
            zeroth_ifd_original[ImageIFD.ZZZTestDFloat],
            zeroth_ifd[ImageIFD.ZZZTestDFloat],
        )

    def test_dump_and_load_specials2(self):
        """test dump and load special types(SingedByte, SiginedShort, DoubleFloat)"""
        zeroth_ifd_original = {
            ImageIFD.ZZZTestSByte: (-128, -128),
            ImageIFD.ZZZTestSShort: (-32768, -32768),
            ImageIFD.ZZZTestDFloat: (1.0e-100, 1.0e-100),
        }
        exif_dict = {"0th": zeroth_ifd_original}
        exif_bytes = piexif.dump(exif_dict)

        exif = piexif.load(exif_bytes)
        zeroth_ifd = exif["0th"]
        self.assertEqual(
            zeroth_ifd_original[ImageIFD.ZZZTestSByte],
            zeroth_ifd[ImageIFD.ZZZTestSByte],
        )
        self.assertEqual(
            zeroth_ifd_original[ImageIFD.ZZZTestSShort],
            zeroth_ifd[ImageIFD.ZZZTestSShort],
        )
        self.assertEqual(
            zeroth_ifd_original[ImageIFD.ZZZTestDFloat],
            zeroth_ifd[ImageIFD.ZZZTestDFloat],
        )

    def test_roundtrip_files(self):
        files = glob.glob(os.path.join("tests", "images", "r_*.jpg"))
        for input_file in files:
            logging.info("loading input file: %s", input_file)
            exif = piexif.load(input_file)
            exif_bytes = piexif.dump(exif)
            o = io.BytesIO()
            piexif.insert(exif_bytes, input_file, o)
            e = piexif.load(o.getvalue())

            t = e.pop("thumbnail")
            thumbnail = exif.pop("thumbnail")
            if t is not None:
                if not (b"\xe0" <= thumbnail[3:4] <= b"\xef"):
                    self.assertEqual(t, thumbnail)
                else:
                    logging.warning(
                        "Given JPEG doesn't follow exif thumbnail standard. "
                        "APPn segments in thumbnail should be removed, "
                        "whereas thumbnail JPEG has it. \n: %s",
                        input_file,
                    )
                exif["1st"].pop(513)
                e["1st"].pop(513)
                exif["1st"].pop(514)
                e["1st"].pop(514)
            for ifd in e:
                if ifd == "0th":
                    if ImageIFD.ExifTag in exif["0th"]:
                        exif["0th"].pop(ImageIFD.ExifTag)
                        e["0th"].pop(ImageIFD.ExifTag)
                    if ImageIFD.GPSTag in exif["0th"]:
                        exif["0th"].pop(ImageIFD.GPSTag)
                        e["0th"].pop(ImageIFD.GPSTag)
                elif ifd == "Exif":
                    if ExifIFD.InteroperabilityTag in exif["Exif"]:
                        exif["Exif"].pop(ExifIFD.InteroperabilityTag)
                        e["Exif"].pop(ExifIFD.InteroperabilityTag)
                for key in exif[ifd]:
                    self.assertEqual(exif[ifd][key], e[ifd][key])

    # transplant ------
    def test_transplant(self):
        piexif.transplant(INPUT_FILE1, INPUT_FILE_PEN, "transplant.jpg")
        i = Image.open("transplant.jpg")
        i.close()
        exif_src = piexif.load(INPUT_FILE1)
        img_src = piexif.load(INPUT_FILE_PEN)
        generated = piexif.load("transplant.jpg")
        self.assertEqual(exif_src, generated)
        self.assertNotEqual(img_src, generated)

        piexif.transplant(INPUT_FILE1, "transplant.jpg")
        self.assertEqual(piexif.load(INPUT_FILE1), piexif.load("transplant.jpg"))
        os.remove("transplant.jpg")

    def test_transplant_m(self):
        """'transplant' on memory."""
        o = io.BytesIO()
        piexif.transplant(I1, I2, o)
        self.assertEqual(piexif.load(I1), piexif.load(o.getvalue()))
        Image.open(o).close()

    def test_transplant_fail1(self):
        with self.assertRaises(ValueError):
            piexif.transplant(I1, I2, False)

    def test_transplant_fail2(self):
        with self.assertRaises(ValueError):
            piexif.transplant(NOEXIF_FILE, I2, "foo.jpg")

    # remove ------
    def test_remove(self):
        piexif.remove(INPUT_FILE1, "remove.jpg")
        exif_dict = piexif.load("remove.jpg")
        none_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "Interop": {},
            "1st": {},
            "thumbnail": None,
        }
        self.assertEqual(exif_dict, none_dict)

        piexif.remove("remove.jpg")
        exif_dict = piexif.load("remove.jpg")
        self.assertEqual(exif_dict, none_dict)
        os.remove("remove.jpg")

    def test_remove2(self):
        with open(INPUT_FILE1, "rb") as f:
            data = f.read()
        with open("remove2.jpg", "wb+") as f:
            f.write(data)
        piexif.remove("remove2.jpg")
        exif_dict = piexif.load("remove2.jpg")
        none_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "Interop": {},
            "1st": {},
            "thumbnail": None,
        }
        self.assertEqual(exif_dict, none_dict)
        os.remove("remove2.jpg")

    def test_remove_m(self):
        """'remove' on memory."""
        o = io.BytesIO()
        with self.assertRaises(ValueError):
            piexif.remove(I1)
        piexif.remove(I1, o)
        exif_dict = piexif.load(o.getvalue())
        none_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "Interop": {},
            "1st": {},
            "thumbnail": None,
        }
        self.assertEqual(exif_dict, none_dict)
        Image.open(o).close()

    # insert ------
    def test_insert(self):
        exif_dict = {"0th": ZEROTH_IFD, "Exif": EXIF_IFD, "GPS": GPS_IFD}
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, INPUT_FILE1, "insert.jpg")
        load_exif_by_PIL("insert.jpg")

        piexif.insert(exif_bytes, NOEXIF_FILE, "insert.jpg")

        with self.assertRaises(ValueError):
            piexif.insert(b"dummy", io.BytesIO())

        piexif.insert(exif_bytes, "insert.jpg")
        os.remove("insert.jpg")

    def test_insert_m(self):
        """'insert' on memory."""
        exif_dict = {"0th": ZEROTH_IFD, "Exif": EXIF_IFD, "GPS": GPS_IFD}
        exif_bytes = piexif.dump(exif_dict)
        o = io.BytesIO()
        piexif.insert(exif_bytes, I1, o)
        self.assertEqual(o.getvalue()[0:2], b"\xff\xd8")
        load_exif_by_PIL(o)

    def test_insert_fail1(self):
        with open(INPUT_FILE1, "rb") as f:
            data = f.read()
        with open("insert.jpg", "wb+") as f:
            f.write(data)
        exif_dict = {"0th": ZEROTH_IFD, "Exif": EXIF_IFD, "GPS": GPS_IFD}
        exif_bytes = piexif.dump(exif_dict)
        with self.assertRaises(ValueError):
            piexif.insert(exif_bytes, INPUT_FILE_TIF)
        os.remove("insert.jpg")

    def test_insert_fail2(self):
        exif_dict = {"0th": ZEROTH_IFD, "Exif": EXIF_IFD, "GPS": GPS_IFD}
        exif_bytes = piexif.dump(exif_dict)
        with self.assertRaises(ValueError):
            piexif.insert(exif_bytes, I1, False)

    # ------
    def test_print_exif(self):
        t = time.time()
        exif = piexif.load(INPUT_FILE_PEN)
        t_cost = time.time() - t
        print(f"'load': {t_cost}[sec]")
        for ifd in ("0th", "Exif", "GPS", "Interop", "1st"):
            print(f"\n{ifd} IFD:")
            data = exif[ifd]
            for key in exif[ifd]:
                print(f" ... {key}, {TAGS[ifd][key]['name']}, {data[key]}")

    # test utility methods----------------------------------------------

    def _compare_value(self, v1, v2, key, ifd):
        fail_msg = f"Unequal for key {ifd}-'{hex(key)}': {v1}, {v2}"
        if type(v1) is not type(v2):
            if isinstance(v1, tuple):
                if isinstance(v2, IFDRational):
                    self.assertEqual(v1[0], v2.numerator, fail_msg)
                    self.assertEqual(v1[1], v2.denominator, fail_msg)
                else:
                    self.assertEqual(pack_byte(*v1), v2, fail_msg)
            elif isinstance(v1, int):
                try:
                    v1_conv = struct.pack("B", v1)
                except Exception:
                    raise ValueError(fail_msg)
                self.assertEqual(v1_conv, v2, fail_msg)
            elif isinstance(v2, int):
                self.assertEqual(struct.pack("B", v2), v1, fail_msg)
            elif isinstance(v1, bytes) and isinstance(v2, str):
                try:
                    self.assertEqual(v1, v2.encode("latin1"), fail_msg)
                except Exception:
                    self.assertEqual(v1, v2, fail_msg)
            else:
                try:
                    self.assertEqual(v1, v2.encode("latin1"), fail_msg)
                except Exception:
                    self.assertEqual(v1, v2, fail_msg)
        else:
            if isinstance(v1, tuple):
                self.assertEqual(len(v1), len(v2), fail_msg)
                for n, (sub_v1, sub_v2) in enumerate(zip(v1, v2)):
                    self._compare_value(sub_v1, sub_v2, key, ifd)
            else:
                self.assertEqual(v1, v2, fail_msg)

    def _compare_piexifDict_PILDict(self, piexifDict, pilDict):
        zeroth_ifd = piexifDict["0th"]
        exif_ifd = piexifDict["Exif"]
        gps_ifd = piexifDict["GPS"]
        if 0xA300 in exif_ifd:
            exif_ifd.pop(0xA300)  # value type is UNDEFINED but PIL returns int

        for key in sorted(zeroth_ifd):
            if key in pilDict:
                if key == 0x8825:
                    continue
                self._compare_value(zeroth_ifd[key], pilDict[key], key, "0th")

        for key in sorted(exif_ifd):
            if key in pilDict:
                self._compare_value(exif_ifd[key], pilDict[key], key, "Exif")

        if 0x8825 in pilDict:
            gps = pilDict.pop(0x8825)
            for key in sorted(gps_ifd):
                if key in gps:
                    self._compare_value(gps_ifd[key], gps[key], key, "GPS")
