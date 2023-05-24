import unittest
import cv2
import numpy as np
import os
from PIL import Image
from bgstools.io.media import load_big_tiff, VideoLoader, convert_image_frame



class VideoLoaderTests(unittest.TestCase):
    def setUp(self):
        self.video_path = 'path/to/big_video.mp4'
        self.video_loader = VideoLoader(self.video_path)
        
        # Open the video file with OpenCV to get the frame info
        cap = cv2.VideoCapture(self.video_path)
        
        # Read the first frame and convert it to a numpy array
        ret, frame = cap.read()
        if ret:  # If a frame has been returned
            self.first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB
            self.expected_height, self.expected_width, self.expected_channels = self.first_frame.shape
        else:
            raise Exception("No frames could be read from the video")

        self.expected_start_frame = 0  # Assuming the video starts from the first frame
        self.expected_end_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Get the total number of frames
        
        cap.release()  # Release the VideoCapture


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
        self.assertTrue(np.array_equal(frame, self.first_frame))

        # Read remaining frames
        count = 1
        while frame is not None:
            count += 1
            frame = self.video_loader.read_frame()

        expected_total_frames = self.expected_end_frame - self.expected_start_frame + 1
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
