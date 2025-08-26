import unittest

from .test_u import UTests
from .test_exif import ExifTests
from .test_helper import HelperTests
from .test_webp import WebpTests


def suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            unittest.makeSuite(UTests),
            unittest.makeSuite(ExifTests),
            unittest.makeSuite(HelperTests),
            unittest.makeSuite(WebpTests),
        ]
    )
    return suite


if __name__ == "__main__":
    unittest.main()
