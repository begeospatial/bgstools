import os
import cv2
import random
import numpy as np
import subprocess
from pathlib import Path 
import json
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

    Raises:
        ValueError: If the provided format is not supported.
    """
    if format.lower() == 'png':
        cv2.imwrite(output_path, frame)
    elif format.lower() in ['jpeg', 'jpg']:
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
    """
    Function to check if an URL is valid or not.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_video_info(video_path: str):
    """
    This function takes the path (or URL) of a video and returns a dictionary with fps and duration information.

    Args:
        video_path (str): The path (or URL) of the video.

    Raises:
        ValueError: If the video doesn't have any frames, or the path/link is incorrect.

    Returns:
        dict: A dictionary containing video information such as fps, duration, frame count, size, codec, video name, and video path.
    """
    cap = cv2.VideoCapture(video_path)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # prevent issues with missing videos
    if int(frame_count) | int(fps) == 0:
        raise ValueError(f"{video_path} doesn't have any frames, check the path/link is correct.")
    else:
        duration = frame_count / fps

    duration_mins = duration / 60

    # Check codec info
    h = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = (chr(h & 0xFF) + chr((h >> 8) & 0xFF) + chr((h >> 16) & 0xFF) + chr((h >> 24) & 0xFF))
  
    # Check if the video is accessible locally
    if os.path.exists(video_path):
        # Store the size of the video
        size = os.path.getsize(video_path)

    # Check if the path to the video is a URL
    elif is_url(video_path):
        # Store the size of the video
        size = urlopen(video_path).length

    # Calculate the size:duration ratio
    sizeGB = size / (1024 * 1024 * 1024)
    size_duration = sizeGB / duration_mins

    return {
        'fps': fps, 
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


def calculate_frames(duration_in_seconds:int, start_time_in_seconds:int, fps:float, n_seconds:int) -> int:
    """ 
    Calculates the number of frames that will be extracted from a video given its duration, start time, frame rate, and the interval at which frames will be extracted.

    Args:
        duration_in_seconds (int): The duration of the video in seconds.
        start_time_in_seconds (int): The start time in seconds from which frames should be extracted.
        fps (float): The frame rate of the video (frames per second).
        n_seconds (int): The interval in seconds at which frames should be extracted from the video.

    Returns:
        int: The number of frames that will be extracted.

    Raises:
        ValueError: If the calculated number of frames is less than 10.
    """
    # Calculate the total number of frames in the video
    total_frames = duration_in_seconds * fps

    # Calculate the starting frame
    start_frame = start_time_in_seconds * fps

    # Calculate the number of frames that will be extracted
    step = n_seconds * fps
    num_frames = (total_frames - start_frame) // step

    # Check if the calculated number of frames is less than 10
    if num_frames < 10:
        raise ValueError("The calculated number of frames is less than 10. Please adjust the input parameters.")

    return num_frames


def select_random_frames(frames:dict, num_frames:int = 10):
    """
    Randomly selects `num_frames` from the `frames` dictionary

    Args:
        frames (dict): Video frames dictionary. Keys are frame numbers and values contain the filepath of the temporal frames.
        num_frames (int): Number of frames to sample. Defaults to 10.

    Returns:
        dict: Dictionary where keys are frame numbers and values are filepaths of the sampled temporal frames.
    """
    if num_frames > len(frames):
        raise ValueError("Number of frames to select is greater than the available frames")

    selected_keys = random.sample(sorted(frames.keys()), num_frames)
    return {key:frames[key] for key in sorted(selected_keys)}


def convert_codec(input_file, output_file, callback:callable=None)->bool:
    """
    Converts video codec from 'hvc1' to 'h264' using FFmpeg.
    This function requires FFmpeg to be installed and in PATH.

    Args:
        input_file (str): The path to the input video file.
        output_file (str): The path to the output video file.
        callback (callable, optional): A callback function to report progress. Defaults to None.
    
    Returns:
        bool: True if successful else False
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


def extract_frames_every_n_seconds(video_filepath: str, frames_dirpath: str, prefix: str, n_seconds: int, start_time_in_seconds: int) -> dict:
    """
    Extracts video frames every `n_seconds` from a video starting from `start_time` and saves them in `output_dir`.

    Args:
        video_filepath (str): Path to the video file.
        frames_dirpath (str): Directory where the extracted frames will be saved.
        prefix (str): Prefix to be used for the frame file names.
        n_seconds (int): The interval in seconds at which frames should be extracted from the video.
        start_time_in_seconds (int): The start time in seconds from which frame extraction should begin.

    Returns:
        dict: A dictionary where the keys are the timestamps and the values are the corresponding frame file paths.
    """
    video_path = Path(video_filepath)
    frames_dir = Path(frames_dirpath)
    frames_dict = {}
    step = n_seconds
    start_time = float(start_time_in_seconds)

    # Check if the video file exists
    if not video_path.is_file():
        raise ValueError(f"Video file not found: {video_filepath}")

    # Check if output directory exists, if not create it
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Get the total duration of the video in seconds
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(video_path)]
    output = subprocess.check_output(cmd).decode('utf-8')
    duration = float(json.loads(output)['format']['duration'])

    # Ensure that the start time is not greater than the total duration of the video
    if start_time > duration:
        raise ValueError(f"Start time {start_time} exceeds video duration {duration}")

    for i in range(int(start_time), int(duration), step):
        frame_file_path = frames_dir / f'{prefix}_{i:06d}_sec.png'
        try:
            subprocess.run(['ffmpeg', '-ss', str(i), '-i', str(video_path), '-frames:v', '1', str(frame_file_path)], check=True)
        except Exception as e:
            raise ValueError(f"Error extracting frame at {i} seconds: {e}")
        else:
            frames_dict[f"SEC_{i:06d}"] = str(frame_file_path)

    return frames_dict



def extract_frames(video_filepath: str, frames_dirpath: str, start_time_in_seconds:int = 1, n_seconds: int = 5,  callback: callable = None, kwargs: dict = None):
    """
    Extract frames from a video file and save them to a specified directory every n seconds starting from a specific time in seconds.

    Args:
        video_filepath (str): Path to the video file.
        frames_dirpath (str): Directory where the extracted frames will be saved.
        
        start_time_in_seconds (int, optional): The time in seconds from where frames should be extracted. Defaults to 1.
        n_seconds (int, optional): The interval in seconds at which frames should be extracted from the video. Defaults to 5.
        callback (callable, optional): A callable object (function) that will be called with the video_info dictionary. Defaults to None.
        **kwargs (dict): Additional arguments as key-value pairs. Defaults to None. Dictionary keys: 'survey_name', 'station_name'. 
            example of kwargs:  {survey_name (str): The name of the survey. , 
                                station_name (str): The name of the station.}

    Returns:
        dict or None: Dictionary mapping from each second mark (for which a frame is extracted) to the corresponding frame file path. None if frame extraction failed.
    """
    # Check if the video file exists
    if video_filepath is None or not os.path.isfile(video_filepath):
        raise ValueError(f"Video file not found: {video_filepath}")

    survey_name = kwargs.get('survey_name')
    station_name = kwargs.get('station_name')

 
    # Get information about the video using the 'get_video_info' function
    video_info = get_video_info(video_path=video_filepath)

    # Call the 'callback' function (if provided) with the video_info dictionary
    if callback is not None:
        callback(video_info)

    # Extract the video_name from the video_filepath
    video_filename = os.path.basename(video_filepath)
    video_name, _ = os.path.splitext(video_filename)

    # Generate prefix string, conditionally including survey and station names
    prefix = f"{survey_name + '_' if survey_name else ''}{station_name + '_' if station_name else ''}{video_name}_frame_"


    # Extract frames from the video using the 'extract_frames_every_n_seconds' function
    # and save them to the specified frames_dirpath
    frames_dict = extract_frames_every_n_seconds(
        video_filepath=video_filepath,
        frames_dirpath=frames_dirpath,
        prefix=prefix,        
        n_seconds=n_seconds,
        start_time_in_seconds=start_time_in_seconds
    )

    # If frames were extracted and saved successfully, return the frames_dict
    if not frames_dict:
        raise Exception(f'Error extracting frames from video: {video_filepath} to {frames_dirpath}. `frames_dict`: {frames_dict}')

    return frames_dict


def load_video(filepath: str) -> bytes:
    """
    Load a video file and return its content as bytes.

    Args:
        filepath (str): Path to the video file.

    Returns:
        bytes: The video content as bytes.
    """
    if not os.path.isfile(filepath):
        raise ValueError(f"File not found: {filepath}")

    with open(filepath, 'rb') as file:
        return file.read()
