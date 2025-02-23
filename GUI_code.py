import tkinter as tk
from tkinter import ttk
from GUI_settings import default_fonts, DefaultTheme, LightTheme, DarkTheme
from UVSim import UVSim
from output_handler import OutputHandler


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
    
    OutputHandler.set_boxes(GUI.output_box, GUI.output_box) #Edit if needed
    simulator = UVSim()
    program = [int(line.strip().lstrip('+')) for line in GUI.read_from_editor() if line.strip()]
    # print(program) #Confirms program is correctly set into the array
    print("running program...")
    GUI.write_to_output("Running program...")

    simulator.load_program(program) #The reason for inputting 1: is because the first instruction is always invalid
    simulator.execute_program()
    GUI.write_to_output("\n") #Separates different program runnings

class GUI():
    """Graphical User Interface class for UVSim."""

    def write_to_output(text: str):
        """Writes text to the output window."""
        GUI.output_box.config(state=tk.NORMAL)
        GUI.output_box.insert(tk.END, text + "\n")
        GUI.output_box.config(state=tk.DISABLED)
        GUI.output_box.yview(tk.END)                #includes a trailing new line char

    def read_from_editor():
        """Reads and returns the text from the editor."""
        return GUI.text_editor.get("1.0", "end-1c").split('\n') # Exclude the trailing newline
    
    def focus_setting_window():
        GUI.setting_frame.lift(GUI.main_frame)

    def focus_main_window():
        GUI.main_frame.lift(GUI.setting_frame)

    def focus_file(button):
        for btn in GUI.file_buttons:
            btn.config(bg=GUI.theme.file_button_color)
        button.config(bg=GUI.theme.file_focus_color)
        button.color = button["background"]

    def create_new_file():
        new_button = tk.Button(GUI.file_header, text=f"    File {len(GUI.file_buttons)+1}    ", bg=GUI.theme.file_button_color, fg=GUI.theme.text_color,activebackground="grey", bd=0)
        new_button.config(command= lambda : GUI.focus_file(new_button))
        new_button.bind('<Enter>', lambda event: GUI.on_hover(event, new_button, GUI.theme.file_button_highlight_color))             
        new_button.bind('<Leave>', lambda event: GUI.on_leave(event, new_button))

        GUI.file_buttons.append(new_button)

        for i, btn in enumerate(GUI.file_buttons):
            btn.grid(row=0, column=i, sticky="ns")

        GUI.focus_file(new_button)

    def on_hover(event, button, color):
        """Changes button color on hover."""
        button.color = button["background"]
        button.config(bg=color)

    def on_leave(event, button):
        """Restores button color when not hovered."""
        button.config(bg=GUI.theme.menu_button_color)

    def clear_output():
        GUI.output_box.config(state=tk.NORMAL)
        GUI.output_box.delete("1.0", tk.END)
        GUI.output_box.config(state=tk.DISABLED)
        GUI.write_to_output("output: ")
    
    def change_theme(name, button):
        if name == LightTheme.name:
            GUI.theme = LightTheme()
        elif name == DarkTheme.name:
            GUI.theme = DarkTheme()
        else:
            GUI.theme = DefaultTheme()

        for btn in GUI.theme_buttons:
            btn.config(font=default_fonts.setting_font)
        button.config(font=default_fonts.setting_selected_font)

    def create_layout_frames(window):
        """Creates the main layout frames (header, editor, terminal)."""

        GUI.setting_frame = tk.Frame(window)
        GUI.setting_frame.place(relx=0,rely=0,relwidth=1, relheight=1)

        setting_header = tk.Frame(GUI.setting_frame, bg=GUI.theme.header_color)
        setting_header.place(relx=0,rely=0,relwidth=1, relheight=.03)

        settings_content_frame = tk.Frame(GUI.setting_frame, bg=GUI.theme.editor_color)
        settings_content_frame.place(relx=0,rely=.03,relwidth=1, relheight=.97)

        GUI.main_frame = tk.Frame(window)
        GUI.main_frame.place(relx=0,rely=0,relwidth=1, relheight=1)

        menu_header = tk.Frame(GUI.main_frame, bg=GUI.theme.header_color)
        menu_header.place(relx=0,rely=0,relwidth=1, relheight=.03)

        GUI.file_header = tk.Frame(GUI.main_frame, bg=GUI.theme.file_header_color)
        GUI.file_header.place(relx=0,rely=.03,relwidth=1, relheight=.03)

        editor = tk.Frame(GUI.main_frame, bg=GUI.theme.editor_color)
        editor.place(relx=0,rely=.06,relwidth=1, relheight=.57)

        terminal = tk.Frame(GUI.main_frame, bg=GUI.theme.output_color)
        terminal.place(relx=0,rely=.63,relwidth=1, relheight=.4)

        return menu_header, GUI.file_header, editor, terminal, setting_header, settings_content_frame

    def create_menu_header(frame):
        """Creates the header menu with Import, Save, and Run buttons."""
        import_button = tk.Button(frame, text="Import", command= lambda: import_prog(), fg=GUI.theme.text_color, font=default_fonts.menu_font, bg=GUI.theme.menu_button_color, bd=0, activebackground="dark grey")
        import_button.place(relx=0,rely=0,relwidth=.05, relheight=1)
        import_button.bind('<Enter>', lambda event: GUI.on_hover(event, import_button, GUI.theme.menu_button_highlight_color))             
        import_button.bind('<Leave>', lambda event: GUI.on_leave(event, import_button))

        save_button = tk.Button(frame, text="Save", command= lambda: save_prog(), fg=GUI.theme.text_color, font=default_fonts.menu_font, bg=GUI.theme.menu_button_color, bd=0, activebackground="grey")
        save_button.place(relx=.05,rely=0,relwidth=.05, relheight=1)
        save_button.bind('<Enter>', lambda event: GUI.on_hover(event, save_button, GUI.theme.menu_button_highlight_color))             
        save_button.bind('<Leave>', lambda event: GUI.on_leave(event, save_button))

        New_file_button = tk.Button(frame, text="New", command= lambda: GUI.create_new_file(), fg=GUI.theme.text_color, font=default_fonts.menu_font, bg=GUI.theme.menu_button_color, bd=0, activebackground="grey")
        New_file_button.place(relx=.1,rely=0,relwidth=.05, relheight=1)
        New_file_button.bind('<Enter>', lambda event: GUI.on_hover(event, New_file_button, GUI.theme.menu_button_highlight_color))             
        New_file_button.bind('<Leave>', lambda event: GUI.on_leave(event, New_file_button))

        setting_button = tk.Button(frame, text="Settings", command= lambda: GUI.focus_setting_window(), fg=GUI.theme.text_color, font=default_fonts.menu_font, bg=GUI.theme.menu_button_color, bd=0, activebackground="light grey")
        setting_button.place(relx=.15,rely=0,relwidth=.08, relheight=1)
        setting_button.bind('<Enter>', lambda event: GUI.on_hover(event, setting_button, GUI.theme.menu_button_highlight_color))             
        setting_button.bind('<Leave>', lambda event: GUI.on_leave(event, setting_button))

        run_button = tk.Button(frame, text="Run", command= lambda: run_prog(), fg=GUI.theme.text_color, font=default_fonts.menu_font, bg=GUI.theme.menu_button_color, bd=0, activebackground="light grey")
        run_button.place(relx=.23,rely=0,relwidth=.05, relheight=1)
        run_button.bind('<Enter>', lambda event: GUI.on_hover(event, run_button, GUI.theme.menu_button_highlight_color))             
        run_button.bind('<Leave>', lambda event: GUI.on_leave(event, run_button))

    def create_file_header(file_header):
        GUI.file_buttons = []

    def create_editor(frame):
        """Creates the text editor with line numbers and scrollbar."""
        #TODO Fix scrollbar sync bug

        def on_scroll(*args):
            GUI.text_editor.yview(*args)
            line_numbers.yview(*args)

        # Create a text box widget
        GUI.text_editor = tk.Text(frame, wrap=tk.WORD, font=default_fonts.editor_font, fg=GUI.theme.text_color, undo=True, bg=GUI.theme.editor_color, bd=0)
        
         # Create a line number text box
        line_numbers = tk.Text(frame, wrap=tk.WORD, font=default_fonts.line_num_font, fg=GUI.theme.text_color, width=4, padx=5, takefocus=0, state=tk.DISABLED, bg=GUI.theme.line_num_color, bd=0)

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
        GUI.output_box = tk.Text(frame, wrap=tk.WORD, fg=GUI.theme.text_color, font=default_fonts.output_font, state=tk.DISABLED, bg=GUI.theme.output_color, bd=0)
        
        # Add a scrollbar
        scrollbar = tk.Scrollbar(frame, command=GUI.output_box.yview)
        GUI.output_box.config(yscrollcommand=scrollbar.set)

        # Pack widgets
        GUI.output_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Function to write text to the output box
        
        GUI.write_to_output("Output:")
        
        GUI.trash_img = tk.PhotoImage(file="trash.png")
        # trash_button = tk.Button(frame, text="🗑", font=("Arial", 20), padx=0, pady=0, command=GUI.clear_output)
        trash_button = tk.Button(GUI.output_box, image=GUI.trash_img, bg=GUI.theme.output_color, activebackground="grey", bd=0, command=GUI.clear_output)
        trash_button.place(relx=1.0, x=-30, rely=0.01)
    
    def create_setting_header(frame):
        save_n_exit_button = tk.Button(frame, text="Save & Exit",bd=0,bg=GUI.theme.menu_button_color, fg=GUI.theme.text_color, command=GUI.focus_main_window)
        save_n_exit_button.place(relx=0,rely=0,relwidth=.1, relheight=1)
        save_n_exit_button.bind('<Enter>', lambda event: GUI.on_hover(event, save_n_exit_button, GUI.theme.file_button_highlight_color))             
        save_n_exit_button.bind('<Leave>', lambda event: GUI.on_leave(event, save_n_exit_button))

    def create_setting_window(frame):
        setting_theme_frame = tk.Frame(frame, bg=GUI.theme.setting_content_color)
        setting_theme_frame.pack(side=tk.TOP, fill=tk.X)
        
        setting_theme_lbl = tk.Label(setting_theme_frame, text="Theme: ", font=('Helvatical bold',int(25)), bg=GUI.theme.setting_content_color,fg = 'black', pady = 10)
        setting_theme_lbl.pack(side=tk.LEFT)

        default_theme_btn = tk.Button(setting_theme_frame, text = 'default', width=int(9), height=int(.5),pady = 10,font=(default_fonts.setting_selected_font if GUI.theme.name == "default_theme" else default_fonts.setting_font))
        default_theme_btn.config(command=lambda: GUI.change_theme("default_theme", default_theme_btn))
        default_theme_btn.pack(side=tk.RIGHT, padx=(5,20))
        
        light_theme_btn = tk.Button(setting_theme_frame, text = 'light', width=int(9), height=int(.5), pady = 10,font=(default_fonts.setting_selected_font if GUI.theme.name == "light_theme" else default_fonts.setting_font))
        light_theme_btn.config(command=lambda: GUI.change_theme("light_theme", light_theme_btn))
        light_theme_btn.pack(side=tk.RIGHT, padx=(5,20))
        
        dark_theme_btn = tk.Button(setting_theme_frame, text = 'dark', width=int(9), height=int(.5), pady = 10,font=(default_fonts.setting_selected_font if GUI.theme.name == "dark_theme" else default_fonts.setting_font))
        dark_theme_btn.config(command=lambda: GUI.change_theme("dark_theme", dark_theme_btn))
        dark_theme_btn.pack(side=tk.RIGHT, padx=(5,20))

        GUI.theme_buttons = []
        GUI.theme_buttons.append(default_theme_btn)
        GUI.theme_buttons.append(light_theme_btn)
        GUI.theme_buttons.append(dark_theme_btn)

def main():
    """Main function to initialize and run the Tkinter GUI."""
    root = tk.Tk() 
    root.title('UVSim') 
    root.geometry('900x600-0+0')    # "-0+0" puts window in top right corner

    GUI.theme = DefaultTheme()

    menu_header, file_header, editor_window, output_window, setting_header, setting_window = GUI.create_layout_frames(root)
    GUI.create_menu_header(menu_header)
    GUI.create_file_header(file_header)
    GUI.create_editor(editor_window)
    GUI.create_output_window(output_window)
    GUI.create_setting_header(setting_header)
    GUI.create_setting_window(setting_window)

    root.mainloop()

if __name__ == "__main__":
    main()
