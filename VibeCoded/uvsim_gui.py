import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import simpledialog
import os
import sys

# --- Import Core Logic and New Modules ---
try:
    from uvsim_core_logic import UVSim
    from uvsim_theme_manager import ThemeManager
    from uvsim_editor_tab import EditorTab
    import uvsim_file_handler as FileHandler # Use module functions
except ImportError as e:
    # Use standard Tkinter messagebox if ttk styles aren't ready
    tk.messagebox.showerror("Initialization Error", f"Could not import required modules: {e}\nPlease ensure all UVSim files (core, theme, editor, file handler) are in the same directory.")
    sys.exit(1)

# --- README Content ---
# Store the README content as a raw multi-line string
# (Raw string r"""...""" prevents issues with backslashes in Markdown)
README_TEXT = r"""
# UVSim IDE - BasicML Simulator

## Overview

This application is a graphical Integrated Development Environment (IDE) for the **UVSim**, a virtual computer simulator. It allows you to write, load, save, and execute programs written in **BasicML (Basic Machine Language)**.

This version of the UVSim operates exclusively in **6-digit mode**, meaning memory words and instructions use a sign followed by 6 digits (e.g., `+100005`, `-000123`). It supports a memory space of 250 words (addresses 000-249) and data values ranging from -999999 to +999999.

The IDE also includes a feature to detect and optionally convert legacy 4-digit BasicML files to the standard 6-digit format upon opening.

## Features

* **Code Editor:** A simple text editor with line numbers for writing 6-digit BasicML code.
* **Tabbed Interface:** Open and work with multiple BasicML files simultaneously.
* **File Operations:** Create new files, open existing files (`.bml`, `.txt`), save, and save-as.
* **4-Digit File Conversion:** Automatically detects legacy 4-digit BasicML files and prompts the user to convert them to 6-digit format, saving the result as a new file.
* **Execution Control:** Run the BasicML program in the active tab and reset the simulator state.
* **State Display:** View the current values of the **Accumulator** and **Program Counter (PC)**.
* **Memory Viewer:** Open a separate window to inspect the contents of all 250 memory locations.
* **Input/Output Panel:** Displays output from the running program (via the `WRITE` instruction) and shows prompts for user input (via the `READ` instruction).
* **Theming:** Switch between a UVU-themed (Green/White) and a Dark theme.

## Prerequisites

* **Python 3:** Ensure you have Python 3 installed (version 3.6 or later recommended).
* **Tkinter:** This GUI library is usually included with standard Python installations. If not, you may need to install it separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu, or it might be included in the Python installer on Windows/macOS).

## How to Use

1.  **Run the IDE:**
    * Navigate to the directory containing the project files in your terminal.
    * Run the command: `python3 uvsim_gui.py`

2.  **Writing BasicML Code:**
    * Use the editor pane to write your program.
    * Each line should contain one 6-digit BasicML word, preceded by a sign (`+` or `-`).
    * Format:
        * **Instructions:** `+OooAaa` (e.g., `+10005` for READ into address 005)
        * **Positive Data:** `+DDDDDD` (e.g., `+000123`)
        * **Negative Data:** `-DDDDDD` (e.g., `-000045`)
    * Lines starting with `#` are comments and are ignored.
    * Empty lines are ignored.
    * The program is loaded into memory starting from address 000. The maximum program size is 250 words.

3.  **BasicML Opcodes (6-Digit):**

    | Opcode | Name         | Description                                      |
    | :----- | :----------- | :----------------------------------------------- |
    | `10`   | `READ`       | Read an integer from user into memory location.  |
    | `11`   | `WRITE`      | Write the value from memory location to output.  |
    | `20`   | `LOAD`       | Load value from memory location into Accumulator. |
    | `21`   | `STORE`      | Store value from Accumulator into memory location.|
    | `30`   | `ADD`        | Add value from memory location to Accumulator.   |
    | `31`   | `SUBTRACT`   | Subtract value from memory location from Accumulator.|
    | `32`   | `DIVIDE`     | Divide Accumulator by value from memory location (integer division). |
    | `33`   | `MULTIPLY`   | Multiply Accumulator by value from memory location.|
    | `40`   | `BRANCH`     | Branch to memory location unconditionally.       |
    | `41`   | `BRANCHNEG`  | Branch if Accumulator is negative.             |
    | `42`   | `BRANCHZERO` | Branch if Accumulator is zero.                 |
    | `43`   | `HALT`       | Halt program execution.                          |

    * `Aaa` in instructions refers to a 3-digit memory address (000-249).

4.  **Loading and Saving:**
    * Use **File -> New** or the "New" button to create an empty tab.
    * Use **File -> Open...** or the "Open" button to load a `.bml` or `.txt` file.
        * If a 4-digit file is detected, you'll be asked if you want to convert and save it as a new 6-digit file (e.g., `original (ported).bml`).
    * Use **File -> Save** / **Save As...** or the "Save" button to save your code. Unsaved tabs will have an asterisk (`*`) next to their name.

5.  **Running and Resetting:**
    * Click the **Run** button or use **Run -> Run Program** (F5) to execute the code in the currently active tab.
        * The simulator will load the code from the editor into memory.
        * Output appears in the "Input/Output Panel".
        * If a `READ` instruction is encountered, a dialog box will pop up asking for input.
        * Execution stops on `HALT` or if an error occurs (e.g., division by zero, invalid memory access, overflow).
    * Click the **Reset** button or use **Run -> Reset Simulator** to clear the simulator's memory, accumulator, and program counter for the active tab. This does *not* clear the editor content.

6.  **Viewing Memory:**
    * Click the **View Memory** button in the state display area or use **View -> View Memory**.
    * This opens a window showing the contents of all 250 memory locations for the simulator associated with the currently active tab.
    * Use the "Refresh" button in the memory view window to update it if the program is running or after reset/load.

## Project File Structure

* `uvsim_gui.py`: The main application file, runs the IDE.
* `uvsim_core_logic.py`: Contains the `UVSim` class implementing the virtual machine logic.
* `uvsim_editor_tab.py`: Defines the `EditorTab` class managing the editor, line numbers, and scrollbars within a tab.
* `uvsim_file_handler.py`: Contains functions for file dialogs and reading/writing files.
* `uvsim_theme_manager.py`: Manages theme definitions and application of styles.
* `uvsim_tests.py`: Unit tests for the core logic and porting functions.

"""


class UVSimIDE(tk.Tk):
    """
    Main application class for the UVSim IDE GUI (Refactored).
    Coordinates ThemeManager, EditorTabs, FileHandler, and UVSim instances.
    """
    MAX_LINES = UVSim.MAX_MEMORY_ADDRESS + 1 # Max lines = Max memory addresses + 1 (250)

    def __init__(self):
        super().__init__()

        self.title("UVSim IDE - BasicML Simulator (6-Digit Mode)")
        self.geometry("800x600")

        # --- Configure Root Window Grid ---
        self.grid_rowconfigure(1, weight=1) # Notebook area expands
        self.grid_columnconfigure(0, weight=1) # Main column expands

        # --- Theme Management ---
        self.style = ttk.Style(self)
        self.theme_manager = ThemeManager(self.style) # Pass style object
        self.current_theme_name = tk.StringVar(value="UVU") # Default theme
        self.current_theme_name.trace_add("write", self._switch_theme) # Update theme when var changes

        # --- Data/State ---
        # tab_data structure:
        # { notebook_tab_id: {
        #      'editor_tab': <EditorTab instance>,
        #      'uvsim_instance': <UVSim instance>,
        #      'file_path': "path/to/file.bml" or None,
        #      'is_saved': True/False,
        #      'original_content': "content when last saved" # For comparison
        #   }, ...
        # }
        self.tab_data = {}
        self.new_file_counter = 0
        self.memory_view_window = None
        self.help_window = None # Reference to the help window
        self._right_clicked_tab_id = None # Store the ID (widget name) of the right-clicked tab

        # --- Initialize UI ---
        self._apply_theme_styles() # Apply initial theme styles
        self._create_menu()
        self._create_toolbar()
        self._create_editor_tabs_notebook() # Creates the ttk.Notebook container
        self._create_tab_context_menu()
        self._create_state_display() # Accumulator, PC, Memory button
        self._create_io_panel()
        self._apply_manual_colors() # Apply colors not handled by styles

        # --- Final Setup ---
        self._add_new_tab() # Start with one empty tab
        self.protocol("WM_DELETE_WINDOW", self._exit_app) # Handle window close button

        # Trigger initial theme application after all widgets potentially exist
        self._switch_theme()


    # --- Theme Handling ---

    def _apply_theme_styles(self):
        """Configures ttk styles using the ThemeManager."""
        theme_name = self.current_theme_name.get()
        self.theme_manager.configure_styles(theme_name)

    def _apply_manual_colors(self):
        """Applies theme colors manually using the ThemeManager."""
        theme_name = self.current_theme_name.get()
        self.theme_manager.apply_manual_colors(self, theme_name) # Pass self (root window)
        # Also apply to help window if open
        if self.help_window and self.help_window.winfo_exists():
             self._apply_theme_to_help_window(theme_name)


    def _switch_theme(self, *args):
        """Applies the selected theme styles and manual colors."""
        self._apply_theme_styles()
        self._apply_manual_colors()
        # Re-apply fixed colors to editor/io panel in case they were affected
        self._reapply_fixed_colors()


    def _reapply_fixed_colors(self):
         """Explicitly re-applies fixed colors that shouldn't change with themes."""
         # IO Panel Text
         if hasattr(self, 'io_text'):
             self.io_text.config(bg=self.theme_manager.IO_TEXT_BG,
                                 fg=self.theme_manager.IO_TEXT_FG)
         # Editor Tabs (handled by EditorTab class using theme_manager constants)
         # Iterate through existing tabs if needed, though EditorTab handles its own bg/fg
         for tab_id in self.notebook.tabs():
             try:
                 data = self._get_tab_data_by_id(tab_id)
                 if data and data['editor_tab']:
                     # EditorTab internally uses theme_manager constants,
                     # so no direct action needed here unless we override them.
                     pass
             except Exception:
                 continue # Ignore errors finding tab data


    # --- UI Creation Methods ---

    def _create_menu(self):
        """Creates the main application menu bar."""
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._add_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._save_current_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_current_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Close Tab", command=self._close_current_tab, accelerator="Ctrl+W")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_app)

        # Edit Menu (Placeholder - Add Cut/Copy/Paste/Undo/Redo later)
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        # Add commands like:
        # edit_menu.add_command(label="Undo", command=lambda: self._pass_edit_command('<<Undo>>'), accelerator="Ctrl+Z")
        # edit_menu.add_command(label="Redo", command=lambda: self._pass_edit_command('<<Redo>>'), accelerator="Ctrl+Y")
        # edit_menu.add_separator()
        # edit_menu.add_command(label="Cut", command=lambda: self._pass_edit_command('<<Cut>>'), accelerator="Ctrl+X")
        # edit_menu.add_command(label="Copy", command=lambda: self._pass_edit_command('<<Copy>>'), accelerator="Ctrl+C")
        # edit_menu.add_command(label="Paste", command=lambda: self._pass_edit_command('<<Paste>>'), accelerator="Ctrl+V")


        # View Menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="View Memory", command=self._show_memory_view)

        # Run Menu
        run_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Program", command=self._run_program, accelerator="F5")
        run_menu.add_command(label="Reset Simulator", command=self._reset_simulator)

        # Help Menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        # --- Added Help Topics Command ---
        help_menu.add_command(label="View Help", command=self._show_help_window)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)

        # --- Keyboard Shortcuts ---
        self.bind_all("<Control-n>", lambda e: self._add_new_tab())
        self.bind_all("<Control-o>", lambda e: self._open_file())
        self.bind_all("<Control-s>", lambda e: self._save_current_file())
        self.bind_all("<Control-S>", lambda e: self._save_current_file_as()) # Ctrl+Shift+S
        self.bind_all("<Control-w>", lambda e: self._close_current_tab())
        self.bind_all("<F5>", lambda e: self._run_program())

    def _create_toolbar(self):
        """Creates the toolbar with action buttons and theme switcher."""
        # Use a standard tk.Frame for the toolbar container
        self.toolbar = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # --- Standard Action Buttons (Left) --- Use ttk.Button with TButton style
        ttk.Button(self.toolbar, text="New", command=self._add_new_tab, style="TButton").pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(self.toolbar, text="Open", command=self._open_file, style="TButton").pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(self.toolbar, text="Save", command=self._save_current_file, style="TButton").pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(self.toolbar, text="Close", command=self._close_current_tab, style="TButton").pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(self.toolbar, text="Run", command=self._run_program, style="TButton").pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(self.toolbar, text="Reset", command=self._reset_simulator, style="TButton").pack(side=tk.LEFT, padx=3, pady=3)

        # --- Theme Switcher Frame (Right) --- Use tk.Frame
        self.theme_switch_frame = tk.Frame(self.toolbar) # Background set by _apply_manual_colors
        self.theme_switch_frame.pack(side=tk.RIGHT, padx=5)

        # --- Theme Radio Buttons (Inside theme frame) --- Use ttk.Radiobutton
        # Note: command is implicitly handled by the trace on current_theme_name
        dark_theme_rb = ttk.Radiobutton(self.theme_switch_frame, text="Dark", variable=self.current_theme_name, value="Dark", style="Toolbar.TRadiobutton")
        dark_theme_rb.pack(side=tk.RIGHT, padx=3, pady=1)
        uvu_theme_rb = ttk.Radiobutton(self.theme_switch_frame, text="UVU", variable=self.current_theme_name, value="UVU", style="Toolbar.TRadiobutton")
        uvu_theme_rb.pack(side=tk.RIGHT, padx=3, pady=1)
        theme_label = ttk.Label(self.theme_switch_frame, text="Theme:", style="TLabel") # Standard label
        theme_label.pack(side=tk.RIGHT, padx=(0, 2), pady=1)


    def _create_editor_tabs_notebook(self):
        """Creates the ttk.Notebook widget to hold editor tabs."""
        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0,0)) # Pad top=0 to connect visually with toolbar
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook.bind("<Button-3>", self._show_tab_context_menu) # Right-click on tab area


    def _create_tab_context_menu(self):
        """Creates the right-click context menu for tabs."""
        self.tab_context_menu = tk.Menu(self, tearoff=0)
        self.tab_context_menu.add_command(label="Close Tab", command=self._close_right_clicked_tab)
        # Colors applied via _apply_manual_colors


    def _create_state_display(self):
        """Creates the area to display Accumulator, PC, and Memory View button."""
        # Use a themed frame
        state_frame = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1, style="TFrame")
        state_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)

        # Labels and Values (Use themed labels)
        ttk.Label(state_frame, text="Accumulator:", style="TLabel").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.acc_value_label = ttk.Label(state_frame, text="+000000", width=10, anchor="e", style="Accent.TLabel") # Use Accent style
        self.acc_value_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(state_frame, text="Program Counter (PC):", style="TLabel").grid(row=0, column=2, padx=15, pady=2, sticky="w")
        self.pc_value_label = ttk.Label(state_frame, text="000", width=5, anchor="e", style="Accent.TLabel") # Use Accent style
        self.pc_value_label.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        # Memory View Button (Themed)
        self.view_mem_button = ttk.Button(state_frame, text="View Memory", command=self._show_memory_view, style="TButton")
        self.view_mem_button.grid(row=0, column=4, padx=15, pady=2, sticky="e")

        # Make the button column expand to push it right
        state_frame.grid_columnconfigure(4, weight=1)


    def _create_io_panel(self):
        """Creates the Input/Output panel at the bottom."""
        # Use themed Labelframe
        io_frame = ttk.LabelFrame(self, text="Input/Output Panel", style="TLabelframe")
        io_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=(0,5)) # Pad bottom=5
        io_frame.grid_rowconfigure(0, weight=1)
        io_frame.grid_columnconfigure(0, weight=1)

        # ScrolledText for output (standard tk widget, styled manually)
        self.io_text = scrolledtext.ScrolledText(
            io_frame,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED, # Start read-only
            # Fixed dark BG/FG applied via _reapply_fixed_colors
            bg=self.theme_manager.IO_TEXT_BG,
            fg=self.theme_manager.IO_TEXT_FG
        )
        self.io_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)


    # --- Tab Management --- (No changes needed in this section)

    def _add_new_tab(self, file_path=None, content=""):
        """Adds a new tab with an EditorTab instance."""
        # Create the EditorTab frame (which builds its own widgets)
        editor_tab = EditorTab(self.notebook, self.theme_manager, self.MAX_LINES)

        # Determine Tab Title and initial state
        if file_path:
            tab_title = os.path.basename(file_path)
            is_saved = True
            original_content = content # Content read from file
            editor_tab.set_content(content)
        else:
            self.new_file_counter += 1
            tab_title = f"Untitled-{self.new_file_counter}"
            file_path = None
            is_saved = False # New files are not saved
            original_content = "" # Empty for new file
            # editor_tab starts empty, no need to set_content("")

        # Add the EditorTab frame to the notebook
        # The notebook uses the widget itself as the identifier
        self.notebook.add(editor_tab, text=tab_title)

        # Create UVSim instance for this tab
        uvsim_instance = UVSim(io_read_func=self._handle_uvsim_read,
                               io_write_func=self._handle_uvsim_write)

        # Store Tab Info using the editor_tab widget as the key in self.tab_data
        tab_id = str(editor_tab) # Get the Tk widget path name as ID
        self.tab_data[tab_id] = {
            'editor_tab': editor_tab,
            'uvsim_instance': uvsim_instance,
            'file_path': file_path,
            'is_saved': is_saved,
            'original_content': original_content
        }

        # Bind modification event directly to the editor *within* the EditorTab
        # Use the tab_id to correctly identify which tab was modified
        editor_tab.editor.bind("<<Modified>>", lambda event, tid=tab_id: self._handle_modification(tid))
        editor_tab.reset_modified_flag() # Ensure starts unmodified

        self.notebook.select(editor_tab) # Make the new tab active
        self._update_tab_title(tab_id)   # Set initial title (with '*' if needed)
        editor_tab.focus()               # Focus the editor in the new tab
        self._update_state_display(uvsim_instance) # Update Acc/PC display


    def _handle_modification(self, tab_id):
        """Handles the <<Modified>> event from an editor to track unsaved changes."""
        data = self.tab_data.get(tab_id)
        if data and data['editor_tab'].winfo_exists():
             # Check the editor's actual modified flag
             if data['editor_tab'].edit_modified():
                 if data['is_saved']: # If it was saved, mark as unsaved
                     data['is_saved'] = False
                     self._update_tab_title(tab_id)
                 # No need to schedule update here, EditorTab handles its internal updates


    def _get_current_tab_id(self):
        """Gets the Tk widget path name (ID) of the currently selected tab."""
        try:
            # notebook.select() returns the widget path name of the selected tab's frame
            return self.notebook.select()
        except tk.TclError:
            return None # No tab selected or notebook doesn't exist

    def _get_tab_data_by_id(self, tab_id):
        """Gets the data dictionary for a given tab ID."""
        return self.tab_data.get(tab_id)

    def _get_current_tab_data(self):
        """Gets the data dictionary for the currently selected tab."""
        current_tab_id = self._get_current_tab_id()
        if current_tab_id:
            return self._get_tab_data_by_id(current_tab_id)
        return None

    def _get_tab_display_name(self, tab_id):
        """Gets the display name for a tab (filename or Untitled-N)."""
        data = self._get_tab_data_by_id(tab_id)
        if not data: return "Unknown"

        if data['file_path']:
            return os.path.basename(data['file_path'])
        else:
            # Retrieve the base name from the notebook tab text if possible
            try:
                # Get current text, remove asterisk if present
                title = self.notebook.tab(tab_id, "text").replace(" *", "")
                # Check if it looks like our default untitled name
                if title.startswith("Untitled-"):
                    return title
            except tk.TclError:
                pass # Fallback if tab doesn't exist anymore

            # Fallback: Generate based on counter or index (less reliable)
            # This part might be less necessary if titles are managed well
            untitled_count = 0
            for tid, tdata in self.tab_data.items():
                if not tdata['file_path'] and tid == tab_id:
                     # Try to find which "Untitled" this is based on its ID order? Complex.
                     # Let's stick to the notebook tab text as the primary source for untitled.
                     # If that fails, maybe return a generic placeholder.
                     return "Untitled" # Simplified fallback
            return "Untitled"


    def _update_tab_title(self, tab_id):
        """Updates the tab title in the notebook, adding/removing '*' for unsaved status."""
        data = self._get_tab_data_by_id(tab_id)
        if not data: return

        base_title = self._get_tab_display_name(tab_id)
        display_title = base_title + ("" if data['is_saved'] else " *")

        try:
            self.notebook.tab(tab_id, text=display_title)
        except tk.TclError:
            # Tab might have been closed between check and update
            # print(f"Warning: Could not update title for tab ID {tab_id}", file=sys.stderr)
            pass


    def _on_tab_changed(self, event=None):
        """Callback when the selected tab changes."""
        current_data = self._get_current_tab_data()
        if current_data:
            # Update Acc/PC display for the newly selected tab's simulator
            self._update_state_display(current_data['uvsim_instance'])
            # Ensure the editor in the selected tab gets focus
            current_data['editor_tab'].focus()
            # Trigger an update for line numbers/scroll sync just in case
            current_data['editor_tab']._schedule_update()
        else:
            # No tab selected (or empty notebook), clear Acc/PC display
            self._update_state_display(None)


    # --- File Operations --- (No changes needed in this section)

    def _open_file(self):
        """Handles File->Open using FileHandler."""
        file_path = FileHandler.ask_open_file(self)
        if not file_path:
            return # User cancelled

        try:
            # 1. Read content using FileHandler
            content, lines = FileHandler.read_file_content(file_path)
            if content is None: return # Error handled by read_file_content (raised exception)

            # 2. Detect format using UVSim's static method
            detected_format = UVSim.detect_format(lines)

            if detected_format == 6:
                # Open directly in a new tab
                self._add_new_tab(file_path=file_path, content=content)
                self._update_io_panel(f"Opened 6-digit file: {os.path.basename(file_path)}")

            elif detected_format == 4:
                # Ask user if they want to port
                base_name = os.path.basename(file_path)
                ported_base_name = base_name.replace('.txt','').replace('.bml','') + " (ported).bml"
                msg = (f"The file '{base_name}' appears to be in the legacy 4-digit format.\n\n"
                       f"Do you want to convert it to the standard 6-digit format?\n\n"
                       f"(A new file named '{ported_base_name}' will be created and opened.)")

                if messagebox.askyesno("Convert 4-digit File?", msg, parent=self):
                    try:
                        # 3. Port using UVSim's static method
                        content_6_digit_lines = UVSim.port_4_to_6(lines)
                        content_6_digit = "\n".join(content_6_digit_lines) # No extra newline needed here

                        # 4. Determine ported file path
                        base, ext = os.path.splitext(file_path)
                        ported_file_path = f"{base} (ported).bml" # Suggest new name

                        # 5. Save the *ported* content using FileHandler
                        if FileHandler.save_content_to_file(ported_file_path, content_6_digit, parent_window=self):
                            # 6. Open the *newly saved* ported file
                            self._add_new_tab(file_path=ported_file_path, content=content_6_digit)
                            self._update_io_panel(f"Ported 4-digit file saved and opened as '{os.path.basename(ported_file_path)}'.")
                        else:
                             # Save failed (error message shown by save_content_to_file)
                             self._update_io_panel(f"Failed to save ported file '{os.path.basename(ported_file_path)}'.")

                    except ValueError as port_err:
                        messagebox.showerror("Porting Error", f"Failed to convert 4-digit file:\n{port_err}", parent=self)
                    except Exception as port_e:
                        messagebox.showerror("Error", f"An unexpected error occurred during porting:\n{port_e}", parent=self)
                else:
                    self._update_io_panel("Opening 4-digit file cancelled by user.") # User chose not to port

        except (IOError, UnicodeDecodeError) as read_err:
            messagebox.showerror("File Error", f"Failed to open file:\n{read_err}", parent=self)
        except ValueError as format_err:
            # Error from detect_format or potentially load_program (though we load later)
            messagebox.showerror("Load Error", f"Cannot process file '{os.path.basename(file_path)}':\n{format_err}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred opening the file:\n{e}", parent=self)
            import traceback
            traceback.print_exc() # Log detailed error


    def _save_file(self, tab_id):
        """
        Saves the content of the specified tab ID to its associated file path.
        If no path exists, calls _save_file_as.

        Args:
            tab_id (str): The ID of the tab to save.

        Returns:
            bool: True if save was successful or not needed, False otherwise.
        """
        data = self._get_tab_data_by_id(tab_id)
        if not data or not data['editor_tab']:
            return False

        if data['is_saved']:
            return True # Already saved

        if data['file_path']:
            # Get current content from the EditorTab instance
            content = data['editor_tab'].get_content().strip() # Strip trailing whitespace/newlines for saving

            # Save using FileHandler
            if FileHandler.save_content_to_file(data['file_path'], content, parent_window=self):
                data['is_saved'] = True
                data['original_content'] = content # Update original content marker
                data['editor_tab'].reset_modified_flag() # Reset editor's internal flag too
                self._update_tab_title(tab_id)
                if tab_id == self._get_current_tab_id():
                    self._update_io_panel(f"File '{os.path.basename(data['file_path'])}' saved.")
                return True
            else:
                # Error message shown by save_content_to_file
                return False
        else:
            # No file path associated, trigger Save As
            return self._save_file_as(tab_id)


    def _save_file_as(self, tab_id):
        """
        Handles 'Save As' for the specified tab ID.

        Args:
            tab_id (str): The ID of the tab to save.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        data = self._get_tab_data_by_id(tab_id)
        if not data or not data['editor_tab']:
            return False

        # Suggest a filename based on the current tab name
        initial_filename = self._get_tab_display_name(tab_id)
        if not data['file_path'] and not initial_filename.endswith(".bml"):
             initial_filename += ".bml" # Add extension if it's an untitled tab

        # Ask for file path using FileHandler
        file_path = FileHandler.ask_save_file_as(self, initial_filename=initial_filename)
        if not file_path:
            return False # User cancelled

        # Get current content
        content = data['editor_tab'].get_content().strip() # Strip trailing whitespace/newlines

        # Save using FileHandler
        if FileHandler.save_content_to_file(file_path, content, parent_window=self):
            # Update tab data with new path and saved state
            data['file_path'] = file_path
            data['is_saved'] = True
            data['original_content'] = content
            data['editor_tab'].reset_modified_flag()
            self._update_tab_title(tab_id) # Update title to reflect new name
            if tab_id == self._get_current_tab_id():
                 self._update_io_panel(f"File saved as '{os.path.basename(file_path)}'.")
            return True
        else:
            # Error message shown by save_content_to_file
            return False

    def _save_current_file(self):
        """Saves the currently active tab."""
        current_tab_id = self._get_current_tab_id()
        if current_tab_id:
            self._save_file(current_tab_id)
        else:
             messagebox.showwarning("Save Error", "No active tab to save.", parent=self)

    def _save_current_file_as(self):
        """Saves the currently active tab using 'Save As'."""
        current_tab_id = self._get_current_tab_id()
        if current_tab_id:
            self._save_file_as(current_tab_id)
        else:
            messagebox.showwarning("Save As Error", "No active tab to save.", parent=self)


    # --- Tab Closing --- (No changes needed in this section)

    def _close_tab(self, tab_id):
        """
        Closes the specified tab ID, prompting to save if needed.
        """
        data = self._get_tab_data_by_id(tab_id)
        if not data or not data['editor_tab']:
            print(f"Debug: Cannot close tab, no data found for ID {tab_id}")
            return # Should not happen if called correctly

        should_close = True
        if not data['is_saved']:
            # Check actual content difference, not just flag, to avoid needless prompts
            current_content = data['editor_tab'].get_content().strip()
            if current_content != data['original_content']:
                tab_name = self._get_tab_display_name(tab_id)
                # Switch focus *before* showing modal dialog
                try: self.notebook.select(tab_id)
                except tk.TclError: pass

                result = messagebox.askyesnocancel("Unsaved Changes",
                                                 f"Save changes to '{tab_name}'?",
                                                 parent=self)
                if result is True: # Yes - Save
                    if not self._save_file(tab_id): # Try saving
                        should_close = False # Save failed or was cancelled
                elif result is None: # Cancel
                    should_close = False
                # Else: No - Don't save, proceed to close
            else:
                 # Content matches original, even if flag is off; reset flag and close
                 data['is_saved'] = True
                 data['editor_tab'].reset_modified_flag()


        if should_close:
            try:
                 editor_tab_widget = data['editor_tab']
                 self.notebook.forget(editor_tab_widget) # Use the widget itself to forget
                 # Clean up data associated with the tab
                 if tab_id in self.tab_data:
                     # Cancel any pending updates for this tab's editor
                     if hasattr(editor_tab_widget, '_update_pending_id') and editor_tab_widget._update_pending_id:
                         editor_tab_widget.after_cancel(editor_tab_widget._update_pending_id)
                     del self.tab_data[tab_id]

                 # If the closed tab was the memory view source, close memory view? Optional.
                 # if self.memory_view_window and hasattr(self.memory_view_window, 'source_tab_id') and self.memory_view_window.source_tab_id == tab_id:
                 #     self._on_memory_view_close()

                 # If no tabs left, maybe add a new default one? Or allow empty state.
                 if len(self.notebook.tabs()) == 0:
                     self._add_new_tab() # Add a fresh tab if the last one is closed

            except tk.TclError as e:
                print(f"Error forgetting tab: {e}", file=sys.stderr)
            except Exception as e:
                 print(f"Error cleaning up tab data: {e}", file=sys.stderr)


    def _close_current_tab(self):
        """Closes the currently active tab."""
        current_tab_id = self._get_current_tab_id()
        if current_tab_id:
            self._close_tab(current_tab_id)
        # else: No tab selected, do nothing


    def _show_tab_context_menu(self, event):
        """Identifies the right-clicked tab ID and shows the context menu."""
        try:
            # Identify the tab index based on event coordinates
            tab_index = self.notebook.index(f"@{event.x},{event.y}")
            # Get the corresponding tab ID (widget path name)
            self._right_clicked_tab_id = self.notebook.tabs()[tab_index]
            # Show the menu
            self.tab_context_menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            self._right_clicked_tab_id = None # Click was not on a tab
        except Exception as e:
            print(f"Error showing context menu: {e}", file=sys.stderr)
            self._right_clicked_tab_id = None


    def _close_right_clicked_tab(self):
        """Closes the tab that was last right-clicked."""
        if self._right_clicked_tab_id:
            # Check if the tab still exists before trying to close
            if self._right_clicked_tab_id in self.tab_data:
                self._close_tab(self._right_clicked_tab_id)
            self._right_clicked_tab_id = None # Reset after action


    # --- UVSim Interaction --- (No changes needed in this section)

    def _update_state_display(self, uvs):
        """Updates the Accumulator and PC labels based on the UVSim instance."""
        if uvs:
            # Use the UVSim's formatting method
            acc_formatted = uvs._format_word(uvs.accumulator)
            pc_formatted = f"{uvs.program_counter:03d}" # PC is always positive 3 digits
            self.acc_value_label.config(text=acc_formatted)
            self.pc_value_label.config(text=pc_formatted)
        else:
            # Default display when no simulator is active
            self.acc_value_label.config(text="+000000")
            self.pc_value_label.config(text="000")

        # Refresh memory view if it's open and linked to this simulator
        self._refresh_memory_view_if_open(uvs)


    def _update_io_panel(self, message):
        """Appends a message to the I/O text panel."""
        try:
            self.io_text.config(state=tk.NORMAL) # Enable writing
            self.io_text.insert(tk.END, str(message) + "\n")
            self.io_text.see(tk.END) # Scroll to the end
            self.io_text.config(state=tk.DISABLED) # Disable writing
        except tk.TclError:
            pass # Ignore if panel destroyed


    def _clear_io_panel(self):
        """Clears the I/O text panel."""
        try:
            self.io_text.config(state=tk.NORMAL)
            self.io_text.delete('1.0', tk.END)
            self.io_text.config(state=tk.DISABLED)
        except tk.TclError:
            pass # Ignore if panel destroyed


    def _handle_uvsim_write(self, value):
        """Callback function passed to UVSim for WRITE operations."""
        # Find which UVSim instance called this (should be the one for the active tab during run)
        # For simplicity, we assume the currently selected tab's simulator is the one running.
        # A more robust approach might involve tracking the running simulator explicitly.
        current_data = self._get_current_tab_data()
        if current_data and current_data['uvsim_instance']:
            uvs = current_data['uvsim_instance']
            display_value = str(value) # BasicML outputs integers
            self._update_io_panel(f"Output: {display_value}")
            # Update state display *after* the operation potentially changes Acc/PC/Memory
            self._update_state_display(uvs)
        else:
            # This case should ideally not happen if run logic is correct
             self._update_io_panel(f"Output (Error: No active simulator context?): {value}")


    def _handle_uvsim_read(self):
        """Callback function passed to UVSim for READ operations."""
        current_data = self._get_current_tab_data()
        if not current_data or not current_data['uvsim_instance']:
            # This indicates a problem - READ called without a context
            messagebox.showerror("Input Error", "Cannot perform READ: No active simulator context.", parent=self)
            raise RuntimeError("READ operation attempted without active simulator.")

        uvs = current_data['uvsim_instance']
        prompt = f"Enter an integer ({UVSim.MIN_WORD_VALUE} to {UVSim.MAX_WORD_VALUE}):"
        self._update_io_panel(f"INPUT Required: {prompt}") # Show prompt in IO panel

        while True:
            # Use simpledialog to get input modally
            value_str = simpledialog.askstring("Input Required", prompt, parent=self)

            if value_str is None:
                # User cancelled the input dialog
                self._update_io_panel("--- Input Cancelled by User ---")
                raise EOFError("Input cancelled by user.") # Signal cancellation to UVSim

            try:
                value = int(value_str)
                # Validate range using UVSim constants
                if not (UVSim.MIN_WORD_VALUE <= value <= UVSim.MAX_WORD_VALUE):
                    raise ValueError(f"Input value {value} is outside the allowed range.")

                # Input is valid
                self._update_io_panel(f"Input received: {value_str}")
                # Update state display (though READ doesn't change Acc/PC directly)
                self._update_state_display(uvs)
                return value # Return the valid integer to UVSim

            except ValueError as e:
                # Show warning if input is not a valid integer or out of range
                messagebox.showwarning("Invalid Input", f"{e}\nPlease try again.", parent=self)
                # Loop continues to ask for input again


    # --- Run and Reset Logic --- (No changes needed in this section)

    def _run_program(self):
        """Loads and runs the program in the currently active tab."""
        current_data = self._get_current_tab_data()
        if not current_data:
            messagebox.showwarning("Run Error", "No active program tab selected.", parent=self)
            return

        editor_tab = current_data['editor_tab']
        uvs = current_data['uvsim_instance']
        if not editor_tab or not uvs:
            messagebox.showerror("Run Error", "Internal error: Missing editor or simulator instance.", parent=self)
            return

        # --- Save Before Running? ---
        # Option 1: Always prompt to save if unsaved
        # Option 2: Run from the editor content directly (current approach)
        # Option 3: Run from the saved file content (requires reading file again)
        # Let's stick with Option 2 for simplicity: run the code currently in the editor.
        # We might want to add a check here if the user prefers to save first.
        # if not current_data['is_saved']:
        #     if not messagebox.askyesno("Run Unsaved Code?", "The code in the editor has unsaved changes. Run the current code anyway?", parent=self):
        #         return # User chose not to run

        # Get code from the editor
        code_content = editor_tab.get_content()
        code_lines = code_content.splitlines()

        # Prepare for run
        self._clear_io_panel()
        self._update_io_panel("--- Running Program (6-Digit Mode) ---")
        try:
            # Reset the simulator associated with this tab
            uvs.reset()
            self._update_state_display(uvs) # Show initial state (PC=0, Acc=0)

            # Load program into the simulator's memory
            uvs.load_program_from_lines(code_lines)
            # Loading successful, update display (PC might still be 0)
            self._update_state_display(uvs)
            self._refresh_memory_view_if_open(uvs) # Update memory view after load

            # Execute the program
            uvs.run() # run() handles the step loop and exception catching internally

            # Program finished (HALT or error handled within run/step)
            if not uvs.is_running: # Should be false after run() finishes
                 if uvs.program_counter == UVSim.MAX_MEMORY_ADDRESS + 1: # Check if halted by PC overflow
                     self._update_io_panel(f"--- Program Execution Halted: PC out of bounds ({uvs.program_counter}) ---")
                 elif any(uvs.memory.get(i, 0) // 1000 == UVSim.HALT for i in range(uvs.MAX_MEMORY_ADDRESS + 1) if i == uvs.program_counter -1): # Simple check if last instruction was HALT
                     self._update_io_panel("--- Program Execution Finished Normally (HALT) ---")
                 # else: Error message was likely printed by step() or run()

        except ValueError as load_err:
            # Error during load_program_from_lines
            self._update_io_panel(f"--- Program Load Failed ---")
            self._update_io_panel(f"Load Error: {load_err}")
            messagebox.showerror("Load Error", f"Failed to load program:\n{load_err}", parent=self)
        except Exception as run_err:
            # Catch unexpected errors during the run setup or if run() re-raises
            self._update_io_panel(f"--- Program Execution Halted Due to Unexpected Error ---")
            self._update_io_panel(f"Error: {run_err}")
            messagebox.showerror("Runtime Error", f"An unexpected error occurred during execution:\n{run_err}", parent=self)
            import traceback
            traceback.print_exc() # Log detailed error

        finally:
            # Ensure final state is displayed, regardless of how execution ended
            self._update_state_display(uvs)
            self._refresh_memory_view_if_open(uvs)


    def _reset_simulator(self):
        """Resets the simulator instance for the currently active tab."""
        current_data = self._get_current_tab_data()
        if not current_data:
            messagebox.showwarning("Reset Error", "No active program tab selected.", parent=self)
            return

        uvs = current_data['uvsim_instance']
        if not uvs:
             messagebox.showerror("Reset Error", "Internal error: Missing simulator instance.", parent=self)
             return

        uvs.reset()
        self._update_state_display(uvs)
        self._clear_io_panel()
        self._update_io_panel("--- Simulator Reset ---")
        self._refresh_memory_view_if_open(uvs)


    # --- Memory View Logic --- (No changes needed in this section)

    def _show_memory_view(self):
        """Creates or focuses the Memory View window for the active tab's simulator."""
        current_data = self._get_current_tab_data()
        current_tab_id = self._get_current_tab_id()

        if not current_data or not current_data['uvsim_instance'] or not current_tab_id:
            messagebox.showwarning("Memory View", "No active simulator tab to view memory for.", parent=self)
            return

        uvs = current_data['uvsim_instance']

        # If window exists, just lift it and refresh for the current UVSim
        if self.memory_view_window and self.memory_view_window.winfo_exists():
            self.memory_view_window.lift()
            # Update the source tab ID and refresh content
            self.memory_view_window.source_tab_id = current_tab_id
            self._update_memory_display(self.memory_view_window.text_widget, uvs)
            self.memory_view_window.title(f"UVSim Memory - {self._get_tab_display_name(current_tab_id)}")
            return

        # --- Create New Memory View Window ---
        self.memory_view_window = tk.Toplevel(self)
        self.memory_view_window.title(f"UVSim Memory - {self._get_tab_display_name(current_tab_id)}")
        self.memory_view_window.geometry("300x500")
        self.memory_view_window.source_tab_id = current_tab_id # Store which tab it belongs to

        # Apply theme colors manually (as it's a Toplevel)
        theme_name = self.current_theme_name.get()
        colors = self.theme_manager.get_theme_colors(theme_name)
        self.memory_view_window.config(bg=colors["mem_view_bg"])

        # Frame inside Toplevel
        mem_frame = ttk.Frame(self.memory_view_window, style="TFrame")
        mem_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        mem_frame.grid_rowconfigure(0, weight=1)
        mem_frame.grid_columnconfigure(0, weight=1) # Make text area expand more

        # ScrolledText for memory display
        mem_text = scrolledtext.ScrolledText(
            mem_frame,
            wrap=tk.NONE,
            state=tk.DISABLED, # Read-only
            # Use specific memory view text colors from theme
            bg=colors["mem_view_text_bg"],
            fg=colors["mem_view_text_fg"]
        )
        mem_text.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.memory_view_window.text_widget = mem_text # Store reference

        # Refresh Button
        refresh_button = ttk.Button(mem_frame, text="Refresh", style="TButton",
                                    command=lambda: self._refresh_memory_view_if_open()) # Refresh based on active tab
        refresh_button.grid(row=1, column=0, pady=5, sticky="e")

        # Close Button
        close_button = ttk.Button(mem_frame, text="Close", style="TButton",
                                  command=self._on_memory_view_close) # Use handler
        close_button.grid(row=1, column=1, pady=5, sticky="w")

        mem_frame.grid_columnconfigure(1, weight=0) # Don't give extra weight to close button col

        # Populate with initial content
        self._update_memory_display(mem_text, uvs)

        # Handle window close button
        self.memory_view_window.protocol("WM_DELETE_WINDOW", self._on_memory_view_close)


    def _update_memory_display(self, text_widget, uvs):
        """Populates the memory view text widget with formatted memory."""
        if not text_widget or not uvs: return

        try:
            text_widget.config(state=tk.NORMAL) # Enable writing
            text_widget.delete('1.0', tk.END)
            mem_content = []
            pc = uvs.program_counter # Highlight the PC location

            for addr in range(uvs.MAX_MEMORY_ADDRESS + 1):
                value = uvs.memory.get(addr, 0)
                formatted_value = uvs._format_word(value) # Use UVSim's formatter
                prefix = "PC->" if addr == pc else "   "
                mem_content.append(f"{prefix}{addr:03d}: {formatted_value}")

            text_widget.insert('1.0', "\n".join(mem_content))

            # Scroll to PC location if possible
            if 0 <= pc <= uvs.MAX_MEMORY_ADDRESS:
                 line_index = f"{pc + 1}.0" # Line numbers are 1-based in Text widget
                 text_widget.see(line_index)
                 # Optional: Add a tag to highlight the PC line
                 text_widget.tag_remove("highlight", "1.0", tk.END)
                 text_widget.tag_add("highlight", line_index, f"{line_index} lineend")
                 text_widget.tag_config("highlight", background="yellow", foreground="black") # Example highlight

        except tk.TclError as e:
            print(f"Error updating memory display: {e}", file=sys.stderr)
        finally:
            if text_widget.winfo_exists():
                text_widget.config(state=tk.DISABLED) # Disable writing


    def _refresh_memory_view_if_open(self, uvs_to_display=None):
        """Refreshes the memory view content if the window is open."""
        if self.memory_view_window and self.memory_view_window.winfo_exists():
            # Determine which UVSim instance to display
            # If an instance is passed, use it. Otherwise, use the current tab's.
            uvs = uvs_to_display
            source_tab_id = None
            if uvs is None:
                current_data = self._get_current_tab_data()
                if current_data and current_data['uvsim_instance']:
                    uvs = current_data['uvsim_instance']
                    source_tab_id = self._get_current_tab_id()
                else:
                    # No active simulator, maybe clear the view or show a message?
                    try:
                        self.memory_view_window.text_widget.config(state=tk.NORMAL)
                        self.memory_view_window.text_widget.delete('1.0', tk.END)
                        self.memory_view_window.text_widget.insert('1.0', "(No active simulator)")
                        self.memory_view_window.text_widget.config(state=tk.DISABLED)
                        self.memory_view_window.title("UVSim Memory")
                    except tk.TclError: pass # Ignore if window closed simultaneously
                    return # Exit if no simulator context

            # Update the display with the determined UVSim instance
            self._update_memory_display(self.memory_view_window.text_widget, uvs)

            # Update title if source tab changed
            if source_tab_id and hasattr(self.memory_view_window, 'source_tab_id') and self.memory_view_window.source_tab_id != source_tab_id:
                 self.memory_view_window.source_tab_id = source_tab_id
                 self.memory_view_window.title(f"UVSim Memory - {self._get_tab_display_name(source_tab_id)}")


    def _on_memory_view_close(self):
        """Callback when the memory view window is closed by user or code."""
        if self.memory_view_window:
            try:
                self.memory_view_window.destroy()
            except tk.TclError:
                pass # Window already destroyed
            finally:
                 self.memory_view_window = None # Clear the reference


    # --- Edit Menu Commands --- (No changes needed in this section)
    def _pass_edit_command(self, command):
         """Sends an edit command (like <<Cut>>, <<Copy>>, <<Paste>>) to the focused widget."""
         try:
             focused_widget = self.focus_get()
             # Check if focus is within an EditorTab's editor
             current_data = self._get_current_tab_data()
             if current_data and focused_widget == current_data['editor_tab'].editor:
                 focused_widget.event_generate(command)
         except Exception as e:
             print(f"Error passing edit command {command}: {e}", file=sys.stderr)


    # --- Help Menu Commands ---

    def _show_about(self):
        """Displays a simple About message box."""
        messagebox.showinfo("About UVSim IDE",
                            "UVSim BasicML Simulator IDE\n"
                            "Refactored Version\n\n"
                            "(Based on UVSim specifications)",
                            parent=self)

    def _show_help_window(self):
        """Creates or focuses the Help window displaying README content."""
        # If window exists, just lift it
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.lift()
            return

        # --- Create New Help Window ---
        self.help_window = tk.Toplevel(self)
        self.help_window.title("UVSim IDE Help")
        self.help_window.geometry("700x550") # Adjust size as needed

        # Apply theme colors manually
        theme_name = self.current_theme_name.get()
        self._apply_theme_to_help_window(theme_name)

        # Frame inside Toplevel
        help_frame = ttk.Frame(self.help_window, style="TFrame", padding=5)
        help_frame.pack(expand=True, fill=tk.BOTH)
        help_frame.grid_rowconfigure(0, weight=1)
        help_frame.grid_columnconfigure(0, weight=1)

        # ScrolledText for help display
        help_text_widget = scrolledtext.ScrolledText(
            help_frame,
            wrap=tk.WORD, # Wrap text
            state=tk.NORMAL, # Start normal to insert text
            padx=5,
            pady=5,
            # Use standard text colors initially, theme applied below
        )
        help_text_widget.grid(row=0, column=0, sticky="nsew")

        # Insert the README content
        help_text_widget.insert(tk.END, README_TEXT.strip()) # Insert stored text

        # Make read-only after inserting
        help_text_widget.config(state=tk.DISABLED)

        # Store reference for theming
        self.help_window.text_widget = help_text_widget

        # Close Button
        close_button = ttk.Button(help_frame, text="Close", style="TButton",
                                  command=self._on_help_window_close)
        close_button.grid(row=1, column=0, pady=(10, 0)) # Add padding below text

        # Handle window close button ('X')
        self.help_window.protocol("WM_DELETE_WINDOW", self._on_help_window_close)

        # Apply theme colors specifically to this window now that widgets exist
        self._apply_theme_to_help_window(theme_name)

    def _apply_theme_to_help_window(self, theme_name):
        """Applies current theme colors to the help window if it exists."""
        if not (self.help_window and self.help_window.winfo_exists()):
            return

        colors = self.theme_manager.get_theme_colors(theme_name)
        # Use standard background/foreground for help window readability
        help_bg = colors.get("mem_view_text_bg", colors["bg"]) # Use text bg or main bg
        help_fg = colors.get("mem_view_text_fg", colors["fg"]) # Use text fg or main fg

        self.help_window.config(bg=help_bg)
        if hasattr(self.help_window, 'text_widget'):
            self.help_window.text_widget.config(bg=help_bg, fg=help_fg)
        # Apply theme to internal frame and button if needed (ttk widgets)
        for child in self.help_window.winfo_children():
             if isinstance(child, ttk.Frame):
                 child.config(style="TFrame") # Re-apply style
             elif isinstance(child, ttk.Button):
                 child.config(style="TButton") # Re-apply style


    def _on_help_window_close(self):
        """Callback when the help window is closed by user or code."""
        if self.help_window:
            try:
                self.help_window.destroy()
            except tk.TclError:
                pass # Window already destroyed
            finally:
                 self.help_window = None # Clear the reference


    # --- Exit Handling --- (No changes needed in this section)
    def _exit_app(self):
        """Handles application exit, checking for unsaved changes across all tabs."""
        unsaved_tabs = []
        # Iterate through a copy of tab IDs as we might modify the dict during save prompts
        tab_ids = list(self.tab_data.keys())

        for tab_id in tab_ids:
            data = self._get_tab_data_by_id(tab_id)
            if data and not data['is_saved']:
                # Also check if content actually differs from original save state
                 current_content = data['editor_tab'].get_content().strip()
                 if current_content != data['original_content']:
                     unsaved_tabs.append(tab_id)

        if not unsaved_tabs:
            self.destroy() # No unsaved changes, exit directly
            return

        # --- Prompt to save unsaved tabs ---
        file_list_str = "\n - ".join([self._get_tab_display_name(tid) for tid in unsaved_tabs])
        msg = f"You have unsaved changes in the following files:\n\n - {file_list_str}\n\nDo you want to save them before exiting?"

        result = messagebox.askyesnocancel("Unsaved Changes", msg, parent=self)

        if result is True: # Yes - Attempt to save all
            all_saved = True
            for tab_id in unsaved_tabs:
                # Ensure tab still exists before trying to save
                if tab_id in self.tab_data:
                    if not self._save_file(tab_id): # Attempt save (will trigger Save As if needed)
                        # Save failed or was cancelled by the user
                        all_saved = False
                        messagebox.showwarning("Exit Cancelled",
                                               f"Save was cancelled or failed for '{self._get_tab_display_name(tab_id)}'.\nExit aborted.",
                                               parent=self)
                        break # Stop trying to save others

            if all_saved:
                self.destroy() # All saves successful, exit

        elif result is False: # No - Discard changes and exit
            self.destroy()

        # Else: Cancel - Do nothing, keep the application open


# --- Main execution ---
if __name__ == "__main__":
    # Set high DPI awareness on Windows if possible
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError):
        pass # Not on Windows or old version

    app = UVSimIDE()
    app.mainloop()
