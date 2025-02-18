import tkinter as tk
from tkinter import ttk

class default_fonts():
    """ font=("FontName", Size, "Style") """
    # style include: "bold", "underline", "italic", "underline", "overstrike"
    menu_font = ('Helvatical',10)
    editor_font = ("Arial", 12)
    line_num_font = ("Arial", 12)
    output_font = ("Arial", 12)

class default_colors():
    """ format: (red,green,blue) ranging from 0-256 """

    #converts rgb into hex
    def rgb_2_hex(r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'
    
    #background colors
    header_color = rgb_2_hex(150, 150, 150)
    editor_color = rgb_2_hex(200, 200, 200)
    line_num_color = rgb_2_hex(190, 190, 190)
    output_color = rgb_2_hex(100, 100, 100)

    #menu button
    menu_button_color = rgb_2_hex(150, 150, 150)
    menu_button_highlight_color = rgb_2_hex(128, 100, 100)
    
    
