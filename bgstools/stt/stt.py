# streamlit tools (stt)
from collections import OrderedDict
from typing import Optional, Tuple
from ..utils import script_as_module
import streamlit as st


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
