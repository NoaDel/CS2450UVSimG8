import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# This module provides functions for handling file operations (open, save)
# It focuses on interacting with the file system and dialogs.
# Format detection and porting logic remain associated with UVSim/GUI.

def ask_open_file(parent_window):
    """
    Shows the 'Open File' dialog and returns the selected file path.

    Args:
        parent_window (tk.Widget): The parent window for the dialog.

    Returns:
        str or None: The full path to the selected file, or None if cancelled.
    """
    file_path = filedialog.askopenfilename(
        title="Open BasicML File",
        filetypes=[("BasicML files", "*.bml *.txt"), ("All files", "*.*")],
        parent=parent_window
    )
    return file_path

def ask_save_file_as(parent_window, initial_filename=""):
    """
    Shows the 'Save File As' dialog and returns the selected file path.

    Args:
        parent_window (tk.Widget): The parent window for the dialog.
        initial_filename (str, optional): A suggested filename. Defaults to "".

    Returns:
        str or None: The full path chosen by the user, or None if cancelled.
    """
    file_path = filedialog.asksaveasfilename(
        title="Save BasicML File As",
        initialfile=initial_filename,
        defaultextension=".bml",
        filetypes=[("BasicML files", "*.bml"), ("Text files", "*.txt"), ("All files", "*.*")],
        parent=parent_window
    )
    return file_path

def read_file_content(file_path):
    """
    Reads the entire content of a text file.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        tuple(str, list[str]) or tuple(None, None):
            A tuple containing (full_content, lines_list) if successful,
            otherwise (None, None).

    Raises:
        IOError: If there's an error reading the file (e.g., permissions).
        UnicodeDecodeError: If the file is not valid UTF-8.
        Exception: For other unexpected errors during file reading.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines() # Keep line endings consistent
            return content, lines
    except (IOError, UnicodeDecodeError) as e:
        # Let the caller handle specific error reporting
        # print(f"Error reading file {file_path}: {e}")
        raise # Re-raise the specific error
    except Exception as e:
        # print(f"Unexpected error reading file {file_path}: {e}")
        raise # Re-raise unexpected errors

def save_content_to_file(file_path, content, parent_window=None):
    """
    Saves string content to a specified file path. Shows error message on failure.

    Args:
        file_path (str): The full path where the file should be saved.
        content (str): The string content to write to the file.
        parent_window (tk.Widget, optional): Parent window for potential error dialogs.

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    try:
        # Ensure content ends with a newline for consistency, unless empty
        if content and not content.endswith('\n'):
            content += '\n'
        elif not content:
             content = "" # Ensure empty content is written as empty file

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"IOError saving file '{os.path.basename(file_path)}': {e}")
        if parent_window:
            messagebox.showerror("Save Error",
                                 f"Failed to save file '{os.path.basename(file_path)}':\n{e}",
                                 parent=parent_window)
        return False
    except Exception as e:
        print(f"Unexpected error saving file '{os.path.basename(file_path)}': {e}")
        if parent_window:
             messagebox.showerror("Error",
                                  f"An unexpected error occurred saving file '{os.path.basename(file_path)}':\n{e}",
                                  parent=parent_window)
        return False

