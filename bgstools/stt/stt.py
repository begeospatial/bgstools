# streamlit tools (stt)
import os
from PIL import Image

from collections import OrderedDict
from typing import Optional, Tuple
from ..utils import script_as_module
import streamlit as st
import hashlib
from typing import Any


def update_session_state(key:str, value:Any)->bool:
    if key not in st.session_state:
        st.session_state[key] = value
    else:
        st.session_state[key] = value
    return True


def build_activities_menu(
    activities_dict: OrderedDict[str, dict], 
    label: str, 
    key: str, 
    services_dirpath: str, 
    disabled: bool = False
) -> Tuple[Optional[str], OrderedDict[str, dict]]:
    """
    Builds an interactive activities menu using Streamlit's sidebar selectbox.

    Args:
        activities_dict (OrderedDict[str, dict]): An ordered dictionary of activities. Each key-value pair corresponds to a 
                                                  service name and its associated information.
        label (str): The label to display above the select box.
        key (str): A unique identifier for the select box widget.
        services_dirpath (str): The directory path where the service resides.
        disabled (bool, optional): Whether the select box is disabled. Defaults to False.

    Returns:
        Tuple[Optional[str], OrderedDict[str, dict]]: The selected activity name and the dictionary of activities. 
                                                      If no activity is selected, the first item in the tuple is None.

    Raises:
        ValueError: If any activity in activities_dict does not have both 'name' and 'url'.
    """
    # Validate that each activity has both 'name' and 'url'
    for task_dict in activities_dict.values():
        if 'name' not in task_dict or 'url' not in task_dict:
            raise ValueError("Each activity dict must have both 'name' and 'url'")

    activity_names = [(task_dict['name'], task_dict['url']) for task_dict in activities_dict.values()]

    selection_tuple = st.sidebar.selectbox(
        label=label,
        index=0,
        options=activity_names,
        format_func=lambda x: x[0],
        key=key,
        disabled=disabled
    )

    if selection_tuple is not None:
        selected_activity, module_filepath = selection_tuple
        script_as_module(module_filepath=module_filepath, services_dirpath=services_dirpath)

    return (selected_activity if selection_tuple else None), activities_dict


def toggle_button(*args, key=None, **kwargs):
    """
    Creates a toggle button that retains its state across reruns of the script.

    The state of the button (pressed/unpressed) is stored in the Streamlit session state
    and is associated with a unique key.

    Parameters:
    *args: The arguments to pass to the Streamlit button function.
    key (str, optional): A unique key for the button. If not provided, a key is generated
        based on the args and kwargs.
    **kwargs: The keyword arguments to pass to the Streamlit button function.

    Returns:
    bool: The current state of the button (True for pressed, False for unpressed).
    """

    # Generate a key from the args and kwargs if none was provided.
    if key is None:
        key = hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()

    try:
        # Set the initial state of the button if it doesn't exist.
        if key not in st.session_state:
            st.session_state[key] = False

        # Set the button type based on the state.
        if "type" not in kwargs:
            kwargs["type"] = "primary" if st.session_state[key] else "secondary"

        # Toggle the state of the button if it's pressed.
        if st.button(*args, **kwargs):
            st.session_state[key] = not st.session_state[key]
            st.experimental_rerun()

    except Exception as e:
        st.error(f"Error occurred: {e}")

    return st.session_state[key]


def display_image_carousel(image_paths_dict: dict, RANDOM_FRAMES:list = []):
    """
    Display an image carousel with navigation slider.

    Args:
        image_paths_dict (dict): Dictionary mapping image titles to their file paths.

    Returns:
        None

    """

    num_images = len(image_paths_dict)
    image_titles = list(image_paths_dict.keys())

    col1, _ = st.columns([2,1])
    with col1:            
        # Create a number input for navigation
        frame_number = st.number_input(label= "**Preview frame:**",  
                                min_value=1,  
                                max_value=num_images,
                                step=1,
                                help="Use to navigate through the available frames.",
                                value=1)
       

        # Get the selected image title and path
        selected_image_title = image_titles[frame_number - 1]
        selected_image_path = image_paths_dict[selected_image_title]
        #
        FRAME_NUMBER = str(frame_number).zfill(2)

    # Load and display the selected image
    if os.path.exists(selected_image_path):
        if selected_image_title in RANDOM_FRAMES:
            st.write(f":star: Frame **{FRAME_NUMBER}** | KEY: **:blue[{selected_image_title}]** | :white_check_mark:")
        else:
            st.write(f":x: Frame **{FRAME_NUMBER}** | KEY: **`{selected_image_title}`**")
        
        # Display the index and title of the selected image

        image = Image.open(selected_image_path)
        # Open the selected image file

        st.image(image, caption=f'Frame {FRAME_NUMBER} | KEY: {selected_image_title}', use_column_width=True)
        # Display the image with its caption

    else:
        st.error(f"Frame image not found: {selected_image_path}")
        # Display an error message if the image file is not found



def video_player(video_filepath, marker_frame_positions=[100, 200, 500, 850, 1100, 1500, 2000, 3000, 4000]):
    """
    Create a custom video player with a timeline and markers for specific frames.
    
    This function is based on the following blog post: https://blog.streamlit.io/introducing-custom-streamlit-components/
    and uses the Plyr video player: https://plyr.io/. 
    NOTE: This function is not currently in Development mode and not fully tested.

    Args:
        video_filepath (str): Path to the video file.
        marker_frame_positions (list): List of frame positions to display markers on the timeline. Defaults to a predefined list.

    Returns:
        None
    """
    
    # Set the page configuration for the Streamlit app
    # st.set_page_config(page_title="Video Player", page_icon=":film_strip", layout="wide")

    # Display the video timeline heading
    st.markdown('## Video timeline')

    # Create the custom component using st.expander
    with st.expander("Show video frames"):
        st.write("""
        <link rel="stylesheet" href="https://cdn.plyr.io/3.6.2/plyr.css" />
        <video id="player" controls crossorigin playsinline>
            <source src="{}" type="video/mp4" />
        </video>

        <script src="https://cdn.plyr.io/3.6.2/plyr.js"></script>
        <script>
            const player = new Plyr('#player');
            var timeline = document.getElementById("timeline");
            var markers = document.getElementsByClassName("marker");
            var currentFrame = 0;
            var currentTime = 0;
            var totalFrames = player.duration * player.fps;
            var totalTime = player.duration;

            // Create the timeline
            for (var i = 0; i < totalFrames; i++) {{
                var tick = document.createElement("div");
                tick.classList.add("tick");
                timeline.appendChild(tick);
            }}

            // Create the markers
            for (var i = 0; i < {}.length; i++) {{
                var marker = document.createElement("div");
                marker.classList.add("marker");
                marker.setAttribute("data-frame", {}[i]);
                timeline.appendChild(marker);
            }}

            // Update the timeline and markers position
            player.on("timeupdate", event => {{
                currentFrame = Math.round(event.detail.plyr.currentTime * player.fps);
                currentTime = event.detail.plyr.currentTime;
                var minutes = Math.floor(currentTime / 60);
                var seconds = Math.floor(currentTime - minutes * 60);
                var time = minutes + ":" + seconds;
                timeline.style.marginLeft = - currentFrame + "px";
                for (var i = 0; i < markers.length; i++){{
                    if (markers[i].getAttribute("data-frame") == currentFrame) {{
                        markers[i].innerHTML = currentFrame + "("+time+")";
                    }}
                }}
            }});
        </script>
        <style>
            /* Add styles for the timeline and markers here */
            timeline {{
                position: relative;
                width: 100%;
                height: 20px;
                overflow: hidden;
            }}
            .tick {{
                position: absolute;
                width: 1px;
                height: 20px;
                background: #ccc;
            }}
            .marker {{
                position:absolute;
                width: 40px;
                height: 20px;
                background: #ff0000;
                color: #fff;
                text-align: center;
                font-size: 12px;
            }}
        </style>
        <div id="timeline"></div>
        """.format(video_filepath, marker_frame_positions, marker_frame_positions), unsafe_allow_html=True)

