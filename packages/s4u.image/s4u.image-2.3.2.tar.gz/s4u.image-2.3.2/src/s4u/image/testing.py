import tempfile
from repoze.filesafe.testing import setupDummyDataManager
from repoze.filesafe.testing import cleanupDummyDataManager
import s4u.sqlalchemy.testing
from s4u.image import configure


GIF = b'GIF89a\x01\x00\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01' \
      b'\x00\x00\x02\x02L\x01\x00;'

PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00' \
      b'\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc' \
      b'\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

JPEG = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00' \
       b'\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t' \
       b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f' \
       b'\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff' \
       b'\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14' \
       b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
       b'\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00' \
       b'\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00' \
       b'?\x00?\xbf\xff\xd9'


class ImageTestCase(s4u.sqlalchemy.testing.DatabaseTestCase):
    """Base class for tests dealing with image models. This base class
    sets up a database with the image tables and configures a
    dummy datamanager so image data does not have to be stored on the
    filesystem.
    """
    def setUp(self):
        super(ImageTestCase, self).setUp()
        setupDummyDataManager()
        tmp = tempfile.gettempdir()
        configure(tmp, tmp)

    def tearDown(self):
        cleanupDummyDataManager()
        super(ImageTestCase, self).tearDown()
        configure(None, None)

__all__ = ['GIF', 'PNG', 'JPEG', 'ImageTestCase']
