# streamlit tools (stt)
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
