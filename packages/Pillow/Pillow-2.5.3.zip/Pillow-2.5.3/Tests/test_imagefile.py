from helper import unittest, PillowTestCase, tearDownModule, lena, fromstring, tostring

from io import BytesIO

from PIL import Image
from PIL import ImageFile
from PIL import EpsImagePlugin


codecs = dir(Image.core)

# save original block sizes
MAXBLOCK = ImageFile.MAXBLOCK
SAFEBLOCK = ImageFile.SAFEBLOCK


class TestImagePutData(PillowTestCase):

    def test_parser(self):

        def roundtrip(format):

            im = lena("L").resize((1000, 1000))
            if format in ("MSP", "XBM"):
                im = im.convert("1")

            file = BytesIO()

            im.save(file, format)

            data = file.getvalue()

            parser = ImageFile.Parser()
            parser.feed(data)
            imOut = parser.close()

            return im, imOut

        self.assert_image_equal(*roundtrip("BMP"))
        self.assert_image_equal(*roundtrip("GIF"))
        self.assert_image_equal(*roundtrip("IM"))
        self.assert_image_equal(*roundtrip("MSP"))
        if "zip_encoder" in codecs:
            try:
                # force multiple blocks in PNG driver
                ImageFile.MAXBLOCK = 8192
                self.assert_image_equal(*roundtrip("PNG"))
            finally:
                ImageFile.MAXBLOCK = MAXBLOCK
        self.assert_image_equal(*roundtrip("PPM"))
        self.assert_image_equal(*roundtrip("TIFF"))
        self.assert_image_equal(*roundtrip("XBM"))
        self.assert_image_equal(*roundtrip("TGA"))
        self.assert_image_equal(*roundtrip("PCX"))

        if EpsImagePlugin.has_ghostscript():
            im1, im2 = roundtrip("EPS")
            # EPS comes back in RGB:
            self.assert_image_similar(im1, im2.convert('L'), 20)

        if "jpeg_encoder" in codecs:
            im1, im2 = roundtrip("JPEG")  # lossy compression
            self.assert_image(im1, im2.mode, im2.size)

        self.assertRaises(IOError, lambda: roundtrip("PDF"))

    def test_ico(self):
        with open('Tests/images/python.ico', 'rb') as f:
            data = f.read()
        p = ImageFile.Parser()
        p.feed(data)
        self.assertEqual((48, 48), p.image.size)

    def test_safeblock(self):

        im1 = lena()

        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        try:
            ImageFile.SAFEBLOCK = 1
            im2 = fromstring(tostring(im1, "PNG"))
        finally:
            ImageFile.SAFEBLOCK = SAFEBLOCK

        self.assert_image_equal(im1, im2)


if __name__ == '__main__':
    unittest.main()

# End of file
