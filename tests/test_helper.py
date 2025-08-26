from __future__ import annotations

import unittest


from piexif import helper


class HelperTests(unittest.TestCase):
    def test_headers(self):
        """Are our headers the correct length?"""
        self.assertEqual(
            len(helper.UserComment._ASCII_PREFIX), helper.UserComment._PREFIX_SIZE
        )
        self.assertEqual(
            len(helper.UserComment._JIS_PREFIX), helper.UserComment._PREFIX_SIZE
        )
        self.assertEqual(
            len(helper.UserComment._UNICODE_PREFIX), helper.UserComment._PREFIX_SIZE
        )
        self.assertEqual(
            len(helper.UserComment._UNDEFINED_PREFIX), helper.UserComment._PREFIX_SIZE
        )

    def test_encode_ascii(self):
        """Do we encode ASCII correctly?"""
        text = "hello world"
        expected = b"\x41\x53\x43\x49\x49\x00\x00\x00hello world"
        actual = helper.UserComment.dump(text, encoding="ascii")
        self.assertEqual(expected, actual)

    def test_decode_ascii(self):
        """Do we decode ASCII correctly?"""
        binary = b"\x41\x53\x43\x49\x49\x00\x00\x00hello world"
        expected = "hello world"
        actual = helper.UserComment.load(binary)
        self.assertEqual(expected, actual)

    def test_encode_jis(self):
        """Do we encode JIS correctly?"""
        text = "\u3053\u3093\u306b\u3061\u306f\u4e16\u754c"
        expected = b"\x4a\x49\x53\x00\x00\x00\x00\x00" + text.encode("shift_jis")
        actual = helper.UserComment.dump(text, encoding="jis")
        self.assertEqual(expected, actual)

    def test_decode_jis(self):
        """Do we decode JIS correctly?"""
        expected = "\u3053\u3093\u306b\u3061\u306f\u4e16\u754c"
        binary = b"\x4a\x49\x53\x00\x00\x00\x00\x00" + expected.encode("shift_jis")
        actual = helper.UserComment.load(binary)
        self.assertEqual(expected, actual)

    def test_encode_unicode(self):
        """Do we encode Unicode correctly?"""
        text = "\u3053\u3093\u306b\u3061\u306f\u4e16\u754c"
        expected = b"\x55\x4e\x49\x43\x4f\x44\x45\x00" + text.encode("utf_16_be")
        actual = helper.UserComment.dump(text, encoding="unicode")
        self.assertEqual(expected, actual)

    def test_decode_unicode(self):
        """Do we decode Unicode correctly?"""
        expected = "\u3053\u3093\u306b\u3061\u306f\u4e16\u754c"
        binary = b"\x55\x4e\x49\x43\x4f\x44\x45\x00" + expected.encode("utf_16_be")
        actual = helper.UserComment.load(binary)
        self.assertEqual(expected, actual)

    def test_encode_bad_encoding(self):
        """De we gracefully handle bad input when encoding?"""
        self.assertRaises(ValueError, helper.UserComment.dump, "hello world", "koi-8r")

    def test_decode_bad_encoding(self):
        """De we gracefully handle bad input when decoding?"""
        self.assertRaises(
            ValueError,
            helper.UserComment.load,
            b"\x00\x00\x00\x00\x00\x00\x00\x00hello",
        )
        self.assertRaises(
            ValueError,
            helper.UserComment.load,
            b"\x12\x34\x56\x78\x9a\xbc\xde\xffhello",
        )
        self.assertRaises(ValueError, helper.UserComment.load, b"hello world")
