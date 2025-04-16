import tkinter as tk
from tkinter import ttk
import sys # For potential error logging

class EditorTab(ttk.Frame):
    """
    Represents a single tab in the UVSim IDE's notebook, containing
    the code editor, line numbers, and scrollbars.
    """

    def __init__(self, parent, theme_manager, max_lines, **kwargs):
        """
        Initializes the EditorTab frame.

        Args:
            parent (tk.Widget): The parent widget (usually the ttk.Notebook).
            theme_manager (ThemeManager): Instance for accessing fixed colors.
            max_lines (int): The maximum number of lines allowed in the editor.
            **kwargs: Additional arguments for the ttk.Frame.
        """
        super().__init__(parent, style="TFrame", **kwargs) # Use themed Frame
        self.theme_manager = theme_manager
        self.max_lines = max_lines
        self._update_pending_id = None

        # --- Create Widgets ---
        self._create_widgets()
        self._layout_widgets()
        self._bind_events()

    def _create_widgets(self):
        """Creates the internal widgets for the editor tab."""
        # Line Numbers Text Area
        self.line_numbers = tk.Text(
            self,
            width=4,          # Fixed width for 3 digits + padding
            padx=3,
            takefocus=0,      # Don't participate in focus traversal
            border=0,
            background=self.theme_manager.LINENUM_BG, # Fixed dark color
            fg=self.theme_manager.LINENUM_FG,         # Fixed dark color
            state='disabled', # Initially read-only
            wrap=tk.NONE      # Prevent line wrapping
        )

        # Main Code Editor Text Area
        self.editor = tk.Text(
            self,
            wrap=tk.NONE,     # Disable line wrapping
            undo=True,        # Enable undo/redo
            bg=self.theme_manager.EDITOR_BG,     # Fixed dark color
            fg=self.theme_manager.EDITOR_FG,     # Fixed dark color
            insertbackground=self.theme_manager.EDITOR_FG # Cursor color
        )

        # Vertical Scrollbar (Themed)
        self.yscroll = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self._on_text_scroll # Custom handler for sync
        )

        # Horizontal Scrollbar (Themed)
        self.xscroll = ttk.Scrollbar(
            self,
            orient=tk.HORIZONTAL,
            command=self.editor.xview # Directly controls editor's xview
        )

        # Configure editor to use scrollbars
        self.editor.config(
            yscrollcommand=self.yscroll.set,
            xscrollcommand=self.xscroll.set
        )

    def _layout_widgets(self):
        """Arranges the widgets within the tab frame using grid."""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1) # Editor row expands vertically
        self.grid_rowconfigure(1, weight=0) # Scrollbar row does not expand
        self.grid_columnconfigure(0, weight=0) # Line numbers col does not expand
        self.grid_columnconfigure(1, weight=1) # Editor col expands horizontally
        self.grid_columnconfigure(2, weight=0) # Scrollbar col does not expand

        # Place widgets
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        self.editor.grid(row=0, column=1, sticky="nsew")
        self.yscroll.grid(row=0, column=2, sticky="ns")
        self.xscroll.grid(row=1, column=0, columnspan=2, sticky="ew") # Span under line# and editor

    def _bind_events(self):
        """Binds events for synchronization and validation."""
        # Modification tracking (used by parent UVSimIDE)
        # The parent will bind to this event on the editor widget directly
        # self.editor.bind("<<Modified>>", self._on_modified) # Example if handled internally

        # Update line numbers/scroll sync when view changes
        self.editor.bind("<Configure>", self._schedule_update) # Editor resized
        self.editor.bind("<FocusIn>", self._schedule_update)   # Gained focus
        self.editor.bind("<KeyRelease>", self._schedule_update) # Text changed

        # Mouse wheel scrolling synchronization
        self.editor.bind("<MouseWheel>", self._on_mouse_wheel)
        self.editor.bind("<Button-4>", self._on_mouse_wheel) # Linux scroll up
        self.editor.bind("<Button-5>", self._on_mouse_wheel) # Linux scroll down
        self.line_numbers.bind("<MouseWheel>", self._on_mouse_wheel)
        self.line_numbers.bind("<Button-4>", self._on_mouse_wheel)
        self.line_numbers.bind("<Button-5>", self._on_mouse_wheel)

        # Line limit validation
        self.editor.bind("<KeyPress-Return>", self._validate_enter_key) # Enter key press
        self.editor.bind("<<Paste>>", self._validate_paste)        # Paste event

    # --- Public Methods ---

    def get_content(self):
        """Returns the entire content of the editor."""
        return self.editor.get("1.0", tk.END)

    def set_content(self, content):
        """Sets the content of the editor, replacing existing content."""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.editor.edit_modified(False) # Reset modified flag after setting content
        self.editor.edit_reset()         # Reset undo stack
        self._schedule_update()          # Update line numbers etc.

    def focus(self):
        """Sets focus to the editor widget."""
        self.editor.focus_set()

    def reset_modified_flag(self):
        """Resets the editor's modified flag."""
        self.editor.edit_modified(False)

    def edit_modified(self, *args):
        """Gets or sets the modified state of the underlying editor widget."""
        return self.editor.edit_modified(*args)

    # --- Event Handlers & Internal Logic ---

    def _schedule_update(self, event=None):
        """Schedules an update for line numbers and scroll sync to avoid excessive updates."""
        # Cancel any pending update
        if self._update_pending_id:
            self.after_cancel(self._update_pending_id)

        # Schedule a new update after a short delay (e.g., 10ms)
        self._update_pending_id = self.after(10, self._perform_update)

    def _perform_update(self):
        """Performs the actual update of line numbers and scroll sync."""
        self._update_pending_id = None # Clear the pending ID
        try:
            if not self.winfo_exists(): # Check if widget still exists
                return
            self._update_line_numbers()
            self._sync_scroll()
            # Reset modified flag *after* potentially updating content/view
            # self.editor.edit_modified(False) # Parent GUI usually handles this based on save state
        except tk.TclError as e:
            # Can happen if widgets are destroyed during update
            # print(f"TclError during scheduled update: {e}", file=sys.stderr)
            pass
        except Exception as e:
            print(f"Error during scheduled update: {e}", file=sys.stderr)

    def _update_line_numbers(self):
        """Redraws the line numbers based on the editor content."""
        try:
            self.line_numbers.config(state=tk.NORMAL) # Enable writing
            self.line_numbers.delete('1.0', tk.END)

            # Get the number of lines currently in the editor
            # 'end-1c' gives the index of the last character, its line number is the count
            last_line_index = self.editor.index('end-1c')
            num_lines = int(last_line_index.split('.')[0]) if last_line_index and '.' in last_line_index else 1

            # Generate line number string (up to max_lines for display consistency)
            # Display numbers 1 to num_lines, but format up to max_lines width if needed
            # We display the actual number of lines present.
            line_numbers_text = "\n".join(f"{i+1:03d}" for i in range(num_lines))

            self.line_numbers.insert('1.0', line_numbers_text)
        except tk.TclError as e:
            # print(f"TclError updating line numbers: {e}", file=sys.stderr)
            pass # Ignore if widget is destroyed
        finally:
            self.line_numbers.config(state=tk.DISABLED) # Disable writing

    def _on_text_scroll(self, *args):
        """
        Handles vertical scrollbar commands, syncing editor and line numbers.
        This is called when the *scrollbar* is moved.
        """
        try:
            # Apply the scroll action to both text widgets
            self.editor.yview(*args)
            self.line_numbers.yview(*args)
        except tk.TclError:
            pass # Ignore if widgets are destroyed

    def _sync_scroll(self):
        """
        Synchronizes the vertical scroll position *from* editor *to* line numbers.
        This is needed when the editor scrolls due to cursor movement, etc.
        """
        try:
            # Get the current scroll position of the editor
            scroll_pos = self.editor.yview()
            # Apply this position to the line numbers widget
            self.line_numbers.yview_moveto(scroll_pos[0])
        except tk.TclError:
             pass # Ignore if widgets are destroyed

    def _on_mouse_wheel(self, event):
        """Handles mouse wheel scrolling over editor or line numbers."""
        # Determine scroll direction (platform-dependent)
        if event.num == 5 or event.delta < 0: # Scroll down
            delta = 1
        elif event.num == 4 or event.delta > 0: # Scroll up
            delta = -1
        else:
            return # Unknown scroll event

        try:
            # Scroll both widgets by the same amount
            self.editor.yview_scroll(delta, "units")
            self.line_numbers.yview_scroll(delta, "units")
        except tk.TclError:
            pass # Ignore if widgets are destroyed

        # Prevent the default scroll behavior which might only scroll the focused widget
        return "break"

    # --- Line Limit Validation ---

    def _get_current_line_count(self):
        """Helper to get the current number of lines in the editor."""
        last_line_index = self.editor.index('end-1c')
        return int(last_line_index.split('.')[0]) if last_line_index and '.' in last_line_index else 1

    def _validate_enter_key(self, event):
        """Prevents adding lines beyond MAX_LINES via the Enter key."""
        current_lines = self._get_current_line_count()
        # Check if adding one more line would exceed the limit
        if current_lines >= self.max_lines:
            # Optionally provide feedback (e.g., status bar message in main GUI)
            # print(f"Line limit ({self.max_lines}) reached.")
            return "break" # Prevents the newline character from being inserted
        return None # Allow the event to proceed

    def _validate_paste(self, event):
        """Prevents pasting text that would exceed MAX_LINES."""
        try:
            clipboard_content = self.editor.clipboard_get()
        except tk.TclError:
            clipboard_content = "" # Handle empty clipboard or error

        lines_in_paste = clipboard_content.count('\n')
        # Add 1 if the clipboard content doesn't end with a newline but has content
        if clipboard_content and not clipboard_content.endswith('\n'):
            lines_in_paste += 1

        # Calculate lines that would be removed by the paste (if text is selected)
        lines_removed = 0
        try:
            sel_start, sel_end = self.editor.tag_ranges(tk.SEL)
            start_line = int(self.editor.index(sel_start).split('.')[0])
            end_line = int(self.editor.index(sel_end).split('.')[0])
            # Adjust if selection ends exactly at the start of a line
            if self.editor.index(sel_end).endswith('.0') and start_line != end_line:
                end_line -= 1
            lines_removed = (end_line - start_line) + 1
        except (ValueError, tk.TclError):
            lines_removed = 0 # No selection or error getting selection

        current_lines = self._get_current_line_count()
        projected_lines = current_lines - lines_removed + lines_in_paste

        if projected_lines > self.max_lines:
            # Provide feedback - ideally through the main GUI's status/IO panel
            print(f"Paste Error: Action would result in {projected_lines} lines, exceeding the {self.max_lines} line limit.")
            # Find the main window to show a message box (requires passing root or using winfo)
            try:
                root = self.winfo_toplevel()
                from tkinter import messagebox # Local import for feedback
                messagebox.showwarning("Paste Error",
                                       f"Pasting this text would exceed the {self.max_lines} line limit.",
                                       parent=root)
            except Exception:
                pass # Ignore if we can't show messagebox

            return "break" # Prevents the paste operation

        return None # Allow the paste event to proceed

