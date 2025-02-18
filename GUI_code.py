import tkinter as tk
from tkinter import ttk 
from GUI_settings import default_colors, default_fonts


# Placeholder functions for import, save, and run actions
# TODO: Replace these with actual implementations

def import_prog():
    """Simulates importing a program. Replace with real import logic."""
    print("importing program...")
    GUI.write_to_output("importing program...")

def save_prog():
    """Simulates saving a program. Replace with real save logic."""
    print("saving program...")
    GUI.write_to_output("saving program...")

def run_prog():
    """Simulates running a program. Replace with actual execution logic."""
    print("running program...")
    code = GUI.read_from_editor()
    GUI.write_to_output(code)
    print(repr(code))

class GUI():
    """Graphical User Interface class for UVSim."""
    def write_to_output(text: str):
        """Writes text to the output window."""
        GUI.output_box.config(state=tk.NORMAL)
        GUI.output_box.insert(tk.END, text + "\n")
        GUI.output_box.config(state=tk.DISABLED)
        GUI.output_box.yview(tk.END)                #includes a trailing new line char

    def read_from_editor() -> str:
        """Reads and returns the text from the editor."""
        return GUI.text_editor.get("1.0", "end-1c")  # Exclude the trailing newline

    def on_hover(event, button):
        """Changes button color on hover."""
        button.config(bg=default_colors.menu_button_highlight_color)

    def on_leave(event, button):
        """Restores button color when not hovered."""
        button.config(bg=default_colors.menu_button_color)

    def create_layout_frames(window):
        """Creates the main layout frames (header, editor, terminal)."""

        header = tk.Frame(window, bg=default_colors.header_color)
        header.place(relx=0,rely=.0,relwidth=1, relheight=.03)

        editor = tk.Frame(window, bg=default_colors.editor_color)
        editor.place(relx=0,rely=.03,relwidth=1, relheight=.6)

        terminal = tk.Frame(window, bg=default_colors.output_color)
        terminal.place(relx=0,rely=.63,relwidth=1, relheight=.37)

        return header, editor, terminal

    def create_header(frame):
        """Creates the header menu with Import, Save, and Run buttons."""
        import_button = tk.Button(frame, text="Import", command= lambda: import_prog(), font=default_fonts.menu_font, bg=default_colors.menu_button_color, bd=0, activebackground="dark grey")
        import_button.place(relx=0,rely=0,relwidth=.05, relheight=1)
        import_button.bind('<Enter>', lambda event: GUI.on_hover(event, import_button))             
        import_button.bind('<Leave>', lambda event: GUI.on_leave(event, import_button))

        save_button = tk.Button(frame, text="Save", command= lambda: save_prog(), font=default_fonts.menu_font, bg=default_colors.menu_button_color, bd=0, activebackground="grey")
        save_button.place(relx=.05,rely=0,relwidth=.05, relheight=1)
        save_button.bind('<Enter>', lambda event: GUI.on_hover(event, save_button))             
        save_button.bind('<Leave>', lambda event: GUI.on_leave(event, save_button))

        run_button = tk.Button(frame, text="Run", command= lambda: run_prog(), font=default_fonts.menu_font, bg=default_colors.menu_button_color, bd=0, activebackground="light grey")
        run_button.place(relx=.1,rely=0,relwidth=.05, relheight=1)
        run_button.bind('<Enter>', lambda event: GUI.on_hover(event, run_button))             
        run_button.bind('<Leave>', lambda event: GUI.on_leave(event, run_button))

    def create_editor(frame):
        """Creates the text editor with line numbers and scrollbar."""
        #TODO Fix scrollbar sync bug

        def on_scroll(*args):
            GUI.text_editor.yview(*args)
            line_numbers.yview(*args)

        # Create a text box widget
        GUI.text_editor = tk.Text(frame, wrap=tk.WORD, font=default_fonts.editor_font, undo=True, bg=default_colors.editor_color, bd=0)
        
         # Create a line number text box
        line_numbers = tk.Text(frame, wrap=tk.WORD, font=default_fonts.line_num_font, width=4, padx=5, takefocus=0, state=tk.DISABLED, bg=default_colors.line_num_color, bd=0)

        # Add a scrollbar widget to the Text widget
        scrollbar = tk.Scrollbar(frame, command=on_scroll)
        GUI.text_editor.config(yscrollcommand=scrollbar.set)
        line_numbers.config(yscrollcommand=scrollbar.set)

        # Pack all the widgets
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        GUI.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def update_line_numbers(event=None):
            """Updates the line number text box."""
            line_numbers.config(state=tk.NORMAL)
            line_numbers.delete("1.0", tk.END)
            
            line_count = GUI.text_editor.get("1.0", tk.END).count("\n")
            line_numbers.insert(tk.END, "\n".join(str(i) for i in range(1, line_count + 1)))
            
            line_numbers.config(state=tk.DISABLED)

        # bind the update_line_numbers whenever the user types
        GUI.text_editor.bind("<KeyPress>", update_line_numbers)
        GUI.text_editor.bind("<KeyRelease>", update_line_numbers)
        
        # Call update_line_numbers initially to show line numbers from the start
        update_line_numbers()

    def create_output_window(frame):
        """Creates the output window with a scrollbar."""

        # Create a text box widget (output window)
        GUI.output_box = tk.Text(frame, wrap=tk.WORD, font=default_fonts.output_font, state=tk.DISABLED, bg=default_colors.output_color)
        
        # Add a scrollbar
        scrollbar = tk.Scrollbar(frame, command=GUI.output_box.yview)
        GUI.output_box.config(yscrollcommand=scrollbar.set)

        # Pack widgets
        GUI.output_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Function to write text to the output box
        
        GUI.write_to_output("output:")

def main():
    """Main function to initialize and run the Tkinter GUI."""
    root = tk.Tk() 
    root.title('UVSim') 
    root.geometry('900x600-0+0')    # "-0+0" puts window in top right corner

    header, editor, terminal = GUI.create_layout_frames(root)
    GUI.create_header(header)
    GUI.create_editor(editor)
    GUI.create_output_window(terminal)

    root.mainloop()


if __name__ == "__main__":
    main()