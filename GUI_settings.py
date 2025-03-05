import tkinter as tk
from tkinter import ttk

class default_fonts():
    """ font=("FontName", Size, "Style") """
    # style include: "bold", "underline", "italic", "underline", "overstrike"
    menu_font = ('Helvatical',9)
    file_header_font = ("Arial", 12)
    editor_font = ("Arial", 12)
    line_num_font = ("Arial", 12)
    output_font = ("Arial", 12)
    setting_font = ("Arial", 12)
    setting_selected_font = ("Arial", 12, "bold")

def rgb_2_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

class DefaultTheme():
    """ Format: (red, green, blue) ranging from 0-256 """

    # UVU dark green = (76,114,29) 
    # UVU white (255,255,255) as the off-color

    name = "default_theme"

    # Background colors
    header_color = rgb_2_hex(76,114,29)
    file_header_color = rgb_2_hex(230, 230, 230)
    editor_color = rgb_2_hex(255, 255, 255)
    line_num_color = rgb_2_hex(220, 230, 220)
    output_color = rgb_2_hex(200, 210, 200)
    setting_content_color = rgb_2_hex(220, 230, 220)

    # Button colors
    menu_button_color = rgb_2_hex(76,114,29)
    menu_button_highlight_color = rgb_2_hex(96,134,49)

    file_button_color = rgb_2_hex(220, 220, 220)
    file_button_highlight_color = rgb_2_hex(180, 180, 180)
    file_focus_color = rgb_2_hex(255, 255, 255)

    # Text color
    text_color = rgb_2_hex(0, 0, 0)

    def __init__(self):
        """color MUST be initialized as a list to make them mutable"""
        # Background colors
        self.header_color = [rgb_2_hex(76,114,29)]
        self.file_header_color = [rgb_2_hex(230, 230, 230)]
        self.editor_color = [rgb_2_hex(255, 255, 255)]
        self.line_num_color = [rgb_2_hex(220, 230, 220)]
        self.output_color = [rgb_2_hex(200, 210, 200)]
        self.setting_content_color = [rgb_2_hex(180, 180, 180)]

        # Button colors
        self.menu_button_color = [rgb_2_hex(76,114,29)]
        self.menu_button_highlight_color = [rgb_2_hex(96,134,49)]

        self.file_button_color = [rgb_2_hex(220, 220, 220)]
        self.file_button_highlight_color = [rgb_2_hex(180, 180, 180)]
        self.file_focus_color = [rgb_2_hex(255, 255, 255)]

        # Text color
        self.text_color = [rgb_2_hex(0, 0, 0)]

class NeutralTheme(DefaultTheme):
    """ Format: (red, green, blue) ranging from 0-256 """
    name = "neutral_theme"

    # Background colors
    header_color = rgb_2_hex(150, 150, 150)
    file_header_color = rgb_2_hex(180, 180, 180)
    editor_color = rgb_2_hex(200, 200, 200)
    line_num_color = rgb_2_hex(190, 190, 190)
    output_color = rgb_2_hex(100, 100, 100)
    setting_content_color = rgb_2_hex(180, 180, 180)

    # Button colors
    menu_button_color = rgb_2_hex(150, 150, 150)
    menu_button_highlight_color = rgb_2_hex(100, 100, 100)

    file_button_color = rgb_2_hex(170, 170, 170)
    file_button_highlight_color = rgb_2_hex(100, 100, 100)
    file_focus_color = rgb_2_hex(200, 200, 200)

    # Text color
    text_color = rgb_2_hex(0, 0, 0)

class LightTheme(DefaultTheme):
    """ Light theme colors with slightly brighter shades """
    name = "light_theme"

    header_color = rgb_2_hex(220, 220, 220)
    file_header_color = rgb_2_hex(240, 240, 240)
    editor_color = rgb_2_hex(255, 255, 255)
    line_num_color = rgb_2_hex(230, 230, 230)
    output_color = rgb_2_hex(180, 180, 180)

    menu_button_color = rgb_2_hex(220, 220, 220)
    menu_button_highlight_color = rgb_2_hex(160, 160, 160)

    file_button_color = rgb_2_hex(230, 230, 230)
    file_button_highlight_color = rgb_2_hex(180, 180, 180)
    file_focus_color = rgb_2_hex(255, 255, 255)
    
    # Text color
    text_color = rgb_2_hex(0, 0, 0)

class DarkTheme(DefaultTheme):
    """ Dark theme colors with deeper, darker shades """
    name = "dark_theme"

    header_color = rgb_2_hex(50, 50, 50)
    file_header_color = rgb_2_hex(55, 55, 55)
    editor_color = rgb_2_hex(80, 80, 80)
    line_num_color = rgb_2_hex(60, 60, 60)
    output_color = rgb_2_hex(50, 50, 50)

    menu_button_color = rgb_2_hex(50, 50, 50)
    menu_button_highlight_color = rgb_2_hex(100, 100, 100)

    file_button_color = rgb_2_hex(70, 70, 75)
    file_button_highlight_color = rgb_2_hex(100, 100, 100)
    file_focus_color = rgb_2_hex(80, 80, 80)
    
    # Text color
    text_color = rgb_2_hex(200, 200, 200)
    
    
