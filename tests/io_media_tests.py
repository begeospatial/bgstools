import unittest
import cv2
import numpy as np
import os
from PIL import Image
from osgeo import gdal
from bgstools.io.media import load_big_tiff, VideoLoader



class VideoLoaderTests(unittest.TestCase):
    def setUp(self):
        self.video_path = 'path/to/big_video.mp4'
        self.video_loader = VideoLoader(self.video_path)

    def tearDown(self):
        self.video_loader.close()

    def test_open(self):
        self.video_loader.open()
        self.assertIsNotNone(self.video_loader.video)

    def test_read_frame(self):
        self.video_loader.open()

        # Read first frame
        frame = self.video_loader.read_frame()
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(frame.shape, (expected_height, expected_width, expected_channels))

        # Read remaining frames
        count = 1
        while frame is not None:
            count += 1
            frame = self.video_loader.read_frame()

        expected_total_frames = expected_end_frame - expected_start_frame
        self.assertEqual(count, expected_total_frames)

    def test_close(self):
        self.video_loader.open()
        self.video_loader.close()
        self.assertIsNone(self.video_loader.video)




class ConvertImageFrameTests(unittest.TestCase):
    def setUp(self):
        self.test_image_path = 'path/to/test_image.jpg'
        self.test_image = cv2.imread(self.test_image_path)

    def tearDown(self):
        pass

    def test_convert_to_png(self):
        output_path = 'output_frame.png'
        convert_image_frame(self.test_image, output_path, format='png')
        self.assertTrue(os.path.isfile(output_path))
        self.assertTrue(Image.open(output_path).format == 'PNG')

        # Clean up
        os.remove(output_path)

    def test_convert_to_jpeg(self):
        output_path = 'output_frame.jpeg'
        convert_image_frame(self.test_image, output_path, format='jpeg', compression=True, jpeg_quality=90)
        self.assertTrue(os.path.isfile(output_path))
        self.assertTrue(Image.open(output_path).format == 'JPEG')

        # Clean up
        os.remove(output_path)

    def test_convert_to_geotiff(self):
        output_path = 'output_frame.tif'
        tiff_metadata = {'Key': 'Value'}
        convert_image_frame(self.test_image, output_path, format='geotiff', tiff_metadata=tiff_metadata)
        self.assertTrue(os.path.isfile(output_path))
        self.assertTrue(gdal.Open(output_path) is not None)

        # Clean up
        os.remove(output_path)


if __name__ == '__main__':
    unittest.main()
