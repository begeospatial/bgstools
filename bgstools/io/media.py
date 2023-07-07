import os
import cv2
import random
import numpy as np
import subprocess 
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen



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


def is_url(url:str):
    """Function to check if an url is valid or not

    Args:
        url (_type_): _description_

    Returns:
        _type_: _description_

    credits: https://github.com/ocean-data-factory-sweden/kso-utils/blob/5aeeb684dd7be86edcc8fbdccac07310f364bba2/tutorials_utils.py
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_video_info(video_path: str):
    """This function takes the path (or url) of a video and returns a dictionary with fps and duration information

    Args:
        video_path (str): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    '''
    
    :param video_path: a string containing the path (or url) where the video of interest can be access from
    :return: Two integers, the fps and duration of the video
    
    modified from: https://github.com/ocean-data-factory-sweden/kso-utils/blob/5aeeb684dd7be86edcc8fbdccac07310f364bba2/movie_utils.py
    '''

    size = 0
    cap = cv2.VideoCapture(video_path)
    # Check video filesize in relation to its duration
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # prevent issues with missing videos
    if int(frame_count)|int(fps) == 0:
        raise ValueError(
            f"{video_path} doesn't have any frames, check the path/link is correct."
        )
    else:
        duration = frame_count / fps

    duration_mins = duration / 60

    ##### Check codec info ########
    h = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = (
        chr(h & 0xFF)
        + chr((h >> 8) & 0xFF)
        + chr((h >> 16) & 0xFF)
        + chr((h >> 24) & 0xFF)
    )
  
    # Check if the video is accessible locally
    if os.path.exists(video_path):
        # Store the size of the video
        size = os.path.getsize(video_path)

    # Check if the path to the video is a url
    elif is_url(video_path):
        # Store the size of the video
        size = urlopen(video_path).length

    # Calculate the size:duration ratio
    sizeGB = size / (1024 * 1024 * 1024)
    size_duration = sizeGB / duration_mins

    return {
        'fps':fps, 
        'duration': duration,
        'frame_count': frame_count,
        'duration_mins': duration_mins,
        'size': size,
        'sizeGB': sizeGB,
        'size_duration': size_duration,
        'codec': codec,
        'video_name': os.path.basename(video_path),
        'video_path': video_path 
        }

def extract_frames_every_n_seconds(video_path:str, output_dir:str, n_seconds:int, total_frames:int, fps:float, prefix: str= 'frame', callback:callable= None)->dict:
    """ Extracts video frames every `n_seconds` and save them in `output_dir` temporary directory.

    Args:
        video_path (str): _description_
        output_dir (str): _description_
        n_seconds (int): _description_
        total_frames (int): _description_
        fps (float): _description_
        prefix (str, optional): _description_. Defaults to 'frame'.

    Returns:
        dict: _description_
    """

    temp_frames = {}
    step = int(n_seconds*fps)
    delete_temp_files = []
    for i in range(0, total_frames, step):
        temp_frames[i] = []
        temp_file_descriptor, temp_file_path = tempfile.mkstemp(prefix=f'{prefix.strip().replace(" ", "_")}%06d_' % i, suffix=f'.png', dir=output_dir)
        os.close(temp_file_descriptor)
        delete_temp_files.append(temp_file_path)
        temp_file_name = os.path.basename(temp_file_path)
        temp_dir_path = os.path.dirname(temp_file_path)
        file_name = f"{temp_file_name.split('_')[0]}.png"
        temp_file_path = os.path.join(temp_dir_path, file_name)

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        
        subprocess.call(['ffmpeg', '-i', video_path, '-vf', 'select=gt(n\,{})'.format(i-1), '-pix_fmt', 'yuv420p', '-vframes', '1', '-f', 'image2', temp_file_path]) 
        temp_frames[i] = temp_file_path
    
    #
    if callback is not None:
        try:
            removed =  [os.remove(file) for file in delete_temp_files]
        except Exception as e:
            callback(f'BGSTOOLS>MEDIA: Error removing temporary files: {e}')
            raise IOError(f'BGSTOOLS>MEDIA: Error removing temporary files: {e}')
        else:
            callback('BGSTOOLS>MEDIA: Temporary files removed successfully')

    return temp_frames


def select_random_frames(frames:dict, num_frames:int = 10):
    """Randomly selects `num_frames` from the `frames` dictionary

    Args:
        frames (dict): video frames dictionary. Keys as frame number and values contain the filepath of the temporal frames
        num_frames (int): number of frames to sample. Defaults to 10.

    Returns:
        dict:  Keys as frame number and values contain the filepath of the sampled temporal frames.
    """
    selected_keys = random.sample(frames.keys(), num_frames)
    return {key:frames[key] for key in selected_keys}


def convert_codec(input_file, output_file, callback:callable=None)->bool:
    """
    Converts video codec from 'hvc1' to 'h264' using FFmpeg.
    This function requires FFmpeg to be installed and in PATH.


    Args:
        input_file (str): The path to the input video file.
        output_file (str): The path to the output video file.
        callback (callable, optional): A callback function to report progress. Defaults to None.
    
    Returns:
        True if successful else False
    """

    # Check if FFmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        message = 'FFmpeg is not installed or is not in PATH'
        print(message)
        if callback: 
            callback(message)        
        return False

    # Check if the input file exists
    if not os.path.isfile(input_file):
        message = f'Input file {input_file} does not exist'
        print(message)
        callback(message)        
        return False

    # Execute FFmpeg command
    try:
        subprocess.run(['ffmpeg', '-i', input_file, '-vcodec', 'libx264', '-acodec', 'copy', '-y', output_file], check=True)
    except subprocess.CalledProcessError as e:
        message = f'Error occurred while converting the file: {e.stderr.decode("utf-8")}'
        print(message)
        callback(message)        
        return False
    else:
        
        return True


def extract_frames(video_filepath, frames_dirpath, callback: callable = None):
    """
    Extract frames from a video file and save them to a specified directory.

    Args:
        video_filepath (str): Path to the video file.
        frames_dirpath (str): Directory where the extracted frames will be saved.
        callback (callable, optional): A callable object (function) that will be called with the video_info dictionary.
                                       Defaults to None.

    Returns:
        list or None: List of temporary frame paths if frames were extracted and saved successfully. None otherwise.
    """

    if video_filepath is not None and os.path.isfile(video_filepath):
        # Check if the video file exists

        video_info = get_video_info(video_path=video_filepath)
        # Get information about the video using the 'get_video_info' function

        if callback is not None:
            callback(video_info)
        # Call the 'callback' function (if provided) with the video_info dictionary

        temp_frames = extract_frames_every_n_seconds(
            video_path=video_filepath,
            output_dir=frames_dirpath,
            n_seconds=5,
            total_frames=video_info['frame_count'],
            fps=video_info['fps']
        )
        # Extract frames from the video using the 'extract_frames_every_n_seconds' function
        # and save them to the specified frames_dirpath

        if temp_frames:
            return temp_frames
        # If frames were extracted and saved successfully, return the temporary frames



def load_video(filepath: str) -> bytes:
    """
    Load a video file and return its content as bytes.

    Args:
        filepath (str): Path to the video file.

    Returns:
        bytes: The content of the video file as bytes.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        AssertionError: If the filepath is not a file.

    """
    assert os.path.isfile(filepath), "File not found: {}".format(filepath)
    # Check if the filepath points to a valid file

    try:
        with open(filepath, 'rb') as video_file:
            video_bytes = video_file.read()
            # Read the content of the video file as bytes
            return video_bytes

    except IOError as e:
        raise IOError("Error loading video file: {}".format(e))
        # Raise an IOError if there's an error reading the video file
