import cv2
import numpy as np


def convert_image_frame(frame, output_path, format='png', compression=False, jpeg_quality=95, tiff_metadata=None):
    """
    Converts an image frame to the specified format (PNG, JPEG, GeoTIFF).

    Args:
        frame (numpy.ndarray): The image frame as a NumPy array.
        output_path (str): The output file path for the converted image.
        format (str, optional): The desired output format. Default is 'png'.
        compression (bool, optional): Whether to apply compression for JPEG format. Default is False.
        jpeg_quality (int, optional): The JPEG quality (0-100) if compression is True. Default is 95.
        tiff_metadata (dict, optional): Metadata to be written for GeoTIFF format. Default is None.

    Usage:
    
        frame = ...  # Image frame as a NumPy array
        output_file_png = 'output_frame.png'
        output_file_jpeg = 'output_frame.jpeg'
        output_file_tiff = 'output_frame.tif'

        convert_image_frame(frame, output_file_png, format='png')
        convert_image_frame(frame, output_file_jpeg, format='jpeg', compression=True, jpeg_quality=90)
        convert_image_frame(frame, output_file_tiff, format='geotiff', tiff_metadata={'Key': 'Value'})

    """
    if format.lower() == 'png':
        cv2.imwrite(output_path, frame)
    elif format.lower() == 'jpeg' or format.lower() == 'jpg':
        if compression:
            params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
            cv2.imwrite(output_path, frame, params)
        else:
            cv2.imwrite(output_path, frame)
    else:
        raise ValueError("Unsupported output format: {}".format(format))




def load_big_tiff(path):
    """
    Loads a big .tiff image using memory-mapped files.

    Args:
        path (str): The path to the .tiff image.

    Returns:
        numpy.ndarray: The image as a NumPy array.
    """
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH)
    return img


class VideoLoader:
    def __init__(self, path):
        """
        Initializes the VideoLoader class.

        Args:
            path (str): The path to the video file.
        """
        self.path = path
        self.video = None
        self.start_frame = 0
        self.end_frame = None

    def open(self):
        """
        Opens the video file and prepares for reading frames.
        """
        self.video = cv2.VideoCapture(self.path)
        total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Adjust end frame if not specified
        if self.end_frame is None:
            self.end_frame = total_frames

        # Validate start and end frames
        self.start_frame = max(0, min(self.start_frame, total_frames - 1))
        self.end_frame = max(self.start_frame + 1, min(self.end_frame, total_frames))

        # Set the starting frame position
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

    def read_frame(self):
        """
        Reads the next frame from the video.

        Returns:
            numpy.ndarray: The frame as a NumPy array.
        """
        if self.video is None or self.video.get(cv2.CAP_PROP_POS_FRAMES) >= self.end_frame:
            return None

        ret, frame = self.video.read()
        return frame if ret else None

    def close(self):
        """
        Closes the video file.
        """
        if self.video is not None:
            self.video.release()
            self.video = None


def export_processed_tiff(image, output_path):
    """
    Exports a processed image as a .tiff file.

    Args:
        image (numpy.ndarray): The processed image as a NumPy array.
        output_path (str): The output file path for the exported .tiff file.
    """
    cv2.imwrite(output_path, image)


