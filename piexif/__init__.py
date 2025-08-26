from ._remove import remove as remove
from ._load import load as load
from ._dump import dump as dump
from ._transplant import transplant as transplant
from ._insert import insert as insert
from ._exif import ExifIFD as ExifIFD
from ._exif import GPSIFD as GPSIFD
from ._exif import ImageIFD as ImageIFD
from ._exif import InteropIFD as InteropIFD
from ._exif import TAGS as TAGS
from ._exif import TYPES as TYPES
from ._exceptions import InvalidImageDataError as InvalidImageDataError


VERSION = "1.1.3"
