import os
import re
import io
import sys
import json
import traceback
from io import StringIO


##################################################################
def extract_section(output, start_marker, end_marker=None, end_alternative=None):
    """
    Extracts a section of text from the provided output based on the given start and end markers.

    Args:
        output (str): The full text from which to extract the section.
        start_marker (str): The marker that indicates the beginning of the section.
        end_marker (str, optional): The marker that indicates the end of the section. Defaults to None.
        end_alternative (str, optional): An alternative marker that can be used if the end_marker is not found. Defaults to None.

    Returns:
        str or None: The extracted section of text, stripped of leading/trailing whitespace, or None if the start_marker is not found.
    """
    start_index = output.find(start_marker)
    if start_index == -1:
        return None
    
    start_index += len(start_marker)
    
    if end_marker:
        end_index = output.find(end_marker, start_index)
        if end_index == -1 and end_alternative:
            end_index = output.find(end_alternative, start_index)
        return output[start_index:end_index].strip() if end_index != -1 else output[start_index:].strip()
    else:
        return output[start_index:].strip()


def extract_all_scripts(output, start_marker, end_marker):
    """
    Extracts all occurrences of code blocks from the provided output based on the given start and end markers.

    Args:
        output (str): The full text from which to extract the code blocks.
        start_marker (str): The marker that indicates the beginning of a code block.
        end_marker (str): The marker that indicates the end of a code block.

    Returns:
        list of str: A list of all extracted code blocks, each stripped of leading/trailing whitespace.
    """
    pattern = re.compile(rf'{re.escape(start_marker)}(.*?){re.escape(end_marker)}', re.DOTALL)
    matches = pattern.findall(output)
    return [match.strip() for match in matches]


def convert_to_json(output):
    """
    Converts the provided output into a JSON-like structure by extracting different sections.

    Args:
        output (str): The full text to be converted into a JSON structure.

    Returns:
        dict: A dictionary with keys 'Instruction', 'Script', 'Assumptions', and 'Data Needed'.
              Each key contains the relevant extracted section, or None if the section is not found.
    """
    instructions_section = extract_section(output, "**Instruction:**", "**Script:**")
    script_sections = extract_all_scripts(output, "**Script:**\n```", "```")
    assumptions_section = extract_section(output, "**Assumptions:**", "**Important note:**")
    data_needed_section = extract_section(output, "**Data needed:**")
    
    json_output = {
        "Instruction": instructions_section.split('\n') if instructions_section else None,
        "Script": "\n".join(script_sections) if script_sections else None,
        "Assumptions": assumptions_section.split('\n') if assumptions_section else None,
        "Data Needed": data_needed_section.split('\n') if data_needed_section else None
    }

    return json_output

def get_error_explanation_and_fix(output):
    
    error_message = extract_section(output, "Error Message Explanation:", "Fixes applied:")
    fixes_applied = extract_section(output, "Fixes applied:", "Final Thought:")


    json_output = {
        "Error Message": error_message.split('\n') if error_message else None,
        "Fixes applied": fixes_applied.split('\n') if fixes_applied else None,
    }

    return json_output


#########################################################################
