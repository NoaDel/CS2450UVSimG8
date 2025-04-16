import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Manages theme definitions and application for the UVSim IDE."""

    # --- Theme Definitions ---
    # Defines color palettes for different themes.
    THEMES = {
        "UVU": {
            "name": "UVU Green", "bg": "#4C721D", "fg": "#FFFFFF", "accent_bg": "#FFFFFF",
            # --- CORRECTED LINE ---
            "accent_fg": "#FFFFFF", # Changed from #4C721D to white for contrast
            # --- END CORRECTION ---
            "disabled_fg": "#A5D6A7", "selected_tab_bg": "#FFFFFF",
            "selected_tab_fg": "#4C721D", "inactive_tab_bg": "#A5D6A7", "inactive_tab_fg": "#FFFFFF",
            "menu_bg": "#4C721D", "menu_fg": "#FFFFFF", "toolbar_bg": "#4C721D",
            "button_bg": "#FFFFFF", "button_fg": "#4C721D", "button_active_bg": "#E0E0E0",
            "radio_select": "#FFFFFF", "state_frame_bg": "#4C721D", "state_label_fg": "#FFFFFF",
            "state_value_fg": "#FFFFFF", "io_frame_bg": "#4C721D", "io_label_fg": "#FFFFFF",
            "mem_view_bg": "#FFFFFF", "mem_view_text_bg": "#FFFFFF", "mem_view_text_fg": "#212121",
        },
        "Dark": {
            "name": "Dark", "bg": "#333333", "fg": "#E0E0E0", "accent_bg": "#555555",
            "accent_fg": "#FFFFFF", "disabled_fg": "#777777", "selected_tab_bg": "#555555",
            "selected_tab_fg": "#FFFFFF", "inactive_tab_bg": "#444444", "inactive_tab_fg": "#AAAAAA",
            "menu_bg": "#333333", "menu_fg": "#E0E0E0", "toolbar_bg": "#333333",
            "button_bg": "#555555", "button_fg": "#FFFFFF", "button_active_bg": "#777777",
            "radio_select": "#FFFFFF", "state_frame_bg": "#333333", "state_label_fg": "#E0E0E0",
            "state_value_fg": "#FFFFFF", "io_frame_bg": "#333333", "io_label_fg": "#E0E0E0",
            "mem_view_bg": "#FFFFFF", "mem_view_text_bg": "#FFFFFF", "mem_view_text_fg": "#212121",
        }
    }

    # --- Fixed Dark Area Colors (Not part of themes, applied directly) ---
    EDITOR_BG = "#2B2B2B"
    EDITOR_FG = "#D3D3D3"
    LINENUM_BG = "#313335"
    LINENUM_FG = "#888888"
    IO_TEXT_BG = "#2B2B2B"
    IO_TEXT_FG = "#D3D3D3"


    def __init__(self, style_object):
        """
        Initializes the ThemeManager.

        Args:
            style_object (ttk.Style): The ttk Style object for the application.
        """
        self.style = style_object
        self.style.theme_use('clam') # Use clam theme as base for customization

    def get_theme_colors(self, theme_name):
        """
        Gets the color dictionary for a given theme name.

        Args:
            theme_name (str): The name of the theme (e.g., "UVU", "Dark").

        Returns:
            dict: A dictionary of color definitions for the theme, or the default
                  theme's colors if the name is not found.
        """
        return self.THEMES.get(theme_name, self.THEMES["UVU"]) # Default to UVU

    def configure_styles(self, theme_name):
        """
        Configures ttk widget styles based on the selected theme.

        Args:
            theme_name (str): The name of the theme to apply styles for.
        """
        colors = self.get_theme_colors(theme_name)

        # --- Configure ttk Styles ---
        # TButton: Standard buttons
        self.style.configure("TButton",
                             foreground=colors["button_fg"],
                             background=colors["button_bg"],
                             bordercolor=colors["accent_fg"], # Border color for buttons
                             padding=2) # Keep small padding for toolbar buttons
        self.style.map("TButton",
                       background=[('active', colors["button_active_bg"])],
                       foreground=[('disabled', colors["disabled_fg"])])

        # TRadiobutton: Theme switcher radio buttons
        self.style.configure("TRadiobutton",
                             foreground=colors["fg"],
                             background=colors["toolbar_bg"], # Match toolbar background
                             padding=1)
        self.style.map("TRadiobutton",
                       background=[('active', colors["button_active_bg"])],
                       indicatorcolor=[('selected', colors["radio_select"])], # Color of the radio circle when selected
                       foreground=[('disabled', colors["disabled_fg"])])
        # Specific style for toolbar radios if needed (inherits TRadiobutton for now)
        self.style.configure("Toolbar.TRadiobutton", background=colors["toolbar_bg"], foreground=colors["fg"])


        # TFrame: Default background for ttk Frames
        self.style.configure("TFrame", background=colors["bg"])

        # TLabel: Default labels
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        # Accent.TLabel: Labels with accent color (e.g., Accumulator/PC values)
        # This now uses the corrected accent_fg from the theme definition
        self.style.configure("Accent.TLabel", background=colors["bg"], foreground=colors["accent_fg"])

        # TNotebook: The main tab container
        self.style.configure("TNotebook", background=colors["bg"], borderwidth=1)
        # TNotebook.Tab: Individual tabs
        self.style.configure("TNotebook.Tab",
                             background=colors["inactive_tab_bg"],
                             foreground=colors["inactive_tab_fg"],
                             padding=[6, 3]) # Padding inside the tab label
        self.style.map("TNotebook.Tab",
                       background=[("selected", colors["selected_tab_bg"])],
                       foreground=[("selected", colors["selected_tab_fg"])],
                       expand=[("selected", [1, 1, 1, 0])]) # Optional slight expansion when selected

        # TLabelframe: Frame with a label (used for I/O Panel)
        self.style.configure("TLabelframe",
                             background=colors["bg"],
                             bordercolor=colors["accent_fg"], # Border color
                             padding=5)
        # TLabelframe.Label: The label text of the TLabelframe
        self.style.configure("TLabelframe.Label",
                             background=colors["bg"], # Match frame background
                             foreground=colors["io_label_fg"]) # Specific color for I/O label

        # TScrollbar (configure if default looks bad with themes)
        # self.style.configure("Vertical.TScrollbar", background=..., troughcolor=...)
        # self.style.configure("Horizontal.TScrollbar", background=..., troughcolor=...)


    def apply_manual_colors(self, root, theme_name):
        """
        Applies theme colors directly to widgets where ttk styles might not
        fully cover or for non-ttk widgets.

        Args:
            root (tk.Tk): The main application window (or relevant container).
            theme_name (str): The name of the theme being applied.
        """
        colors = self.get_theme_colors(theme_name)

        # Apply to root window background
        root.config(bg=colors["bg"])

        # Apply to specific standard tk widgets or containers if needed
        # Example: Toolbar (tk.Frame)
        if hasattr(root, 'toolbar'):
            root.toolbar.config(bg=colors["toolbar_bg"])

        # Example: Theme Switcher Frame (tk.Frame inside toolbar)
        if hasattr(root, 'theme_switch_frame'):
             root.theme_switch_frame.config(bg=colors["toolbar_bg"]) # Match toolbar

        # Example: Menu Bar (tk.Menu)
        if hasattr(root, 'menu_bar'):
            root.menu_bar.config(bg=colors["menu_bg"], fg=colors["menu_fg"])
            # Apply to sub-menus as well
            for menu_child in root.menu_bar.winfo_children():
                if isinstance(menu_child, tk.Menu):
                    menu_child.config(bg=colors["menu_bg"], fg=colors["menu_fg"])

        # Example: Tab Context Menu (tk.Menu)
        if hasattr(root, 'tab_context_menu'):
            root.tab_context_menu.config(bg=colors["menu_bg"], fg=colors["menu_fg"])

        # Apply themed colors to Memory View (if open) - This needs to be called
        # from the main GUI when the theme changes and the window exists.
        if hasattr(root, 'memory_view_window') and root.memory_view_window and root.memory_view_window.winfo_exists():
            root.memory_view_window.config(bg=colors["mem_view_bg"])
            if hasattr(root.memory_view_window, 'text_widget'):
                # Apply specific memory view text area colors from theme
                root.memory_view_window.text_widget.config(
                    bg=colors["mem_view_text_bg"],
                    fg=colors["mem_view_text_fg"]
                )

        # --- Apply Fixed Dark Colors to Specific Areas ---
        # These are applied regardless of the theme selected.
        # Note: These are best applied when the widgets are *created*.
        # This section is more of a reminder of where these colors are used.

        # Example: IO Text Area (scrolledtext.ScrolledText)
        if hasattr(root, 'io_text'):
             root.io_text.config(bg=self.IO_TEXT_BG, fg=self.IO_TEXT_FG)

        # Editor and Line Numbers are handled within EditorTab creation.

