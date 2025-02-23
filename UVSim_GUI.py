import sys
import os
import queue
import tempfile
import threading
from tkinter import ttk, filedialog, messagebox
from GUI_settings import *
from io import StringIO
import contextlib

class UVSim:
    def __init__(self, gui):
        self.gui = gui  # Store the GUI instance
        self.memory = [0] * 100
        self.accumulator = 0
        self.instruction_counter = 0

    def load_program(self, program):
        for i, instruction in enumerate(program):
            self.memory[i] = instruction

    # I/O Operations
    def read(self, operand):
        def get_input():
            print("get_input called")
            self.gui.output_box.config(state="normal")
            # Set index *before* prompt, but *after* any previous content:
            self.gui.input_start_index = self.gui.output_box.index(tk.END)
            self.gui.output_box.insert(tk.END, "Please type an integer: ")
            self.gui.output_box.see(tk.END)
            self.gui.wait_for_input_ready()  # Wait for input
            input_value = self.gui.output_queue.get()
            print(f"UVSim.read got input: '{input_value}'")

            try:
                value = int(input_value)
                self.memory[operand] = value
            except ValueError:
                self.gui.write_to_output("Error: Invalid input. Please enter an integer.")
                get_input()  # Get input again
            finally:
                self.gui.output_box.config(state="disabled") # prevent typing when no prompt

        get_input()

    def write(self, operand):
        self.gui.write_to_output(str(self.memory[operand]))

    # Load/Store Operations
    def load(self, operand):
        self.accumulator = self.memory[operand]

    def store(self, operand):
        self.memory[operand] = self.accumulator

    # Arithmetic Operations
    def add(self, operand):
        self.accumulator += self.memory[operand]
        if not (-9999 <= self.accumulator <= 9999):
            print("Error: Overflow during addition.")
            return False
        return True

    def subtract(self, operand):
        self.accumulator -= self.memory[operand]
        if not (-9999 <= self.accumulator <= 9999):
            print("Error: Overflow during subtraction.")
            return False
        return True

    def divide(self, operand):
        if self.memory[operand] == 0:
            print("Error: Division by zero.")
            return False
        self.accumulator //= self.memory[operand]
        return True

    def multiply(self, operand):
        self.accumulator *= self.memory[operand]
        if not (-9999 <= self.accumulator <= 9999):
            print("Error: Overflow during multiplication.")
            return False
        return True

    # Control Operations
    def branch(self, operand):
        self.instruction_counter = operand

    def branchneg(self, operand):
        if self.accumulator < 0:
            self.instruction_counter = operand

    def branchzero(self, operand):
        if self.accumulator == 0:
            self.instruction_counter = operand

    def halt(self, operand):
        print("Program halted.")
        return False  # Signal to stop execution

    def execute_program(self):
        while True:
            if self.instruction_counter >= len(self.memory):
                self.gui.write_to_output("Error: Instruction counter out of bounds.")
                break  # Halt if instruction counter goes out of memory bounds.
            instruction = self.memory[self.instruction_counter]
            opcode = instruction // 100
            operand = instruction % 100

            self.instruction_counter += 1

            if opcode == 10:
                print(f"Calling read with operand: {operand}")  # Add this
                self.read(operand)
            elif opcode == 11:
                self.write(operand)
            elif opcode == 20:
                self.load(operand)
            elif opcode == 21:
                self.store(operand)
            elif opcode == 30:
                if not self.add(operand):
                    break
            elif opcode == 31:
                if not self.subtract(operand):
                    break
            elif opcode == 32:
                if not self.divide(operand):
                    break
            elif opcode == 33:
                if not self.multiply(operand):
                    break
            elif opcode == 40:
                self.branch(operand)
            elif opcode == 41:
                self.branchneg(operand)
            elif opcode == 42:
                self.branchzero(operand)
            elif opcode == 43:
                if self.halt(operand) == False:
                    break
            else:
                print("Error: Invalid opcode.")
                break

            if not -9999 <= self.accumulator <= 9999:
                print("Error: Accumulator overflow.")
                return

class GUI:
    """Graphical User Interface class for UVSim."""

    output_box = None
    output_queue = queue.Queue()
    input_ready = None  # Add input_ready attribute
    input_entered = None  # Add input_entered attribute
    theme = DefaultTheme()  # Initialize theme here
    file_buttons = [] # Initialize file_buttons here

    def __init__(self, root):
        """Initialize the GUI with a Tkinter root window."""
        self.theme_buttons = None
        self.root = root
        self.theme = DefaultTheme()  # Initialize theme here
        self.output_box = None  # these need to be initialized
        self.output_queue = queue.Queue()
        self.input_ready = threading.Event()
        self.file_buttons = []
        self.create_widgets()
        self.input_entered = tk.BooleanVar(value=False)

    def create_widgets(self):
        """Creates all the widgets and layouts for the GUI."""

        self.setting_frame = tk.Frame(self.root)
        self.setting_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        setting_header = tk.Frame(self.setting_frame, bg=self.theme.header_color)
        setting_header.place(relx=0, rely=0, relwidth=1, relheight=.03)

        settings_content_frame = tk.Frame(self.setting_frame, bg=self.theme.editor_color)
        settings_content_frame.place(relx=0, rely=.03, relwidth=1, relheight=.97)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        menu_header = tk.Frame(self.main_frame, bg=self.theme.header_color)
        menu_header.place(relx=0, rely=0, relwidth=1, relheight=.03)

        self.file_header = tk.Frame(self.main_frame, bg=self.theme.file_header_color)
        self.file_header.place(relx=0, rely=.03, relwidth=1, relheight=.03)

        editor = tk.Frame(self.main_frame, bg=self.theme.editor_color)
        editor.place(relx=0, rely=.06, relwidth=1, relheight=.57)

        terminal = tk.Frame(self.main_frame, bg=self.theme.output_color)
        terminal.place(relx=0, rely=.63, relwidth=1, relheight=.4)

        self.create_menu_header(menu_header)
        self.create_file_header(self.file_header)
        self.create_editor(editor)
        self.create_output_window(terminal)
        self.create_setting_header(setting_header)
        self.create_setting_window(settings_content_frame)

    def style_button(self, button, type="file"):
        """Applies common styles to a button."""
        if type == "menu":
            button.config(
                bg=self.theme.menu_button_color,
                fg=self.theme.text_color,
                font=default_fonts.menu_font,
                bd=0,
                activebackground="grey"
            )
            button.bind('<Enter>', lambda event: self.on_hover(event, button, self.theme.menu_button_highlight_color))
            button.bind('<Leave>', lambda event: self.on_leave(event, button))
        else:   #file
            button.config(
                bg=self.theme.file_button_color,
                fg=self.theme.text_color,
                bd=0,
                activebackground="grey"
            )
            button.bind('<Enter>', lambda event: self.on_hover(event, button, self.theme.file_button_highlight_color))
            button.bind('<Leave>', lambda event: self.on_leave(event, button))

    def import_prog(self):
        """Imports a program from a text file."""
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    program_text = file.read()
                    self.text_editor.delete("1.0", tk.END)  # Clear existing text
                    self.text_editor.insert("1.0", program_text)
            except FileNotFoundError:
                print(f"Error: File not found: {file_path}")
            except Exception as e:
                print(f"Error importing program: {e}")

    def save_prog(self):
        """Saves the program from the editor to a text file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as file:
                    program_text = self.text_editor.get("1.0", tk.END)
                    file.write(program_text)
            except Exception as e:
                print(f"Error saving program: {e}")

    def run_prog(self):
        """Runs the program in the GUI's editor."""
        program_text = self.text_editor.get("1.0", tk.END)
        program = []
        for line in program_text.splitlines():
            line = line.strip()
            if line:  # Ignore empty lines
                try:
                    program.append(int(line))
                except ValueError:
                    messagebox.showerror("Error", f"Invalid instruction: {line}")
                    return  # Stop if there's an invalid instruction

        simulator = UVSim(self)
        simulator.load_program(program)
         # Create a thread to run UVSim
        thread = threading.Thread(target=simulator.execute_program)
        thread.start()

    def execute_uvsim(self, temp_file_name):
        """Executes UVSim in a separate thread."""
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            try:
                simulator = UVSim(self)  # Pass self (GUI instance) to UVSim constructor
                program = read_file(temp_file_name)
                if program is not None:
                    simulator.load_program(program)
                    simulator.execute_program()
                else:
                    self.write_to_output("Error: Could not read program.")
            except Exception as e:
                self.write_to_output(f"Error running program: {e}")

        os.remove(temp_file_name)

        # Display the output in the GUI thread
        self.root.after(0, self.write_to_output, temp_stdout.getvalue())

    def write_to_output(self, text: str):
        """Writes text to the output window."""
        self.output_box.config(state=tk.NORMAL)
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)  # Scroll to the end
        self.output_box.config(state=tk.DISABLED) #Set output box back to disabled.

    def read_from_editor(self) -> str:
        """Reads and returns the text from the editor."""
        return self.text_editor.get("1.0", "end-1c")  # Exclude the trailing newline

    def focus_setting_window(self):
        """Brings the settings window to the front."""
        self.setting_frame.lift(self.main_frame)

    def focus_main_window(self):
        """Brings the main window to the front."""
        self.main_frame.lift(self.setting_frame)

    def focus_file(self, button):
        """Highlights the clicked file button."""
        for btn in self.file_buttons:
            btn.config(bg=self.theme.file_button_color)
        button.config(bg=self.theme.file_focus_color)
        button.color = button["background"]

    def create_new_file(self):
        """Creates a new file button in the file header."""
        new_button = tk.Button(self.file_header, text=f"    File {len(self.file_buttons) + 1}    ")
        self.style_button(new_button)
        new_button.config(command=lambda: self.focus_file(new_button))
        self.file_buttons.append(new_button)

        # Re-grid buttons to accommodate the new one
        for i, btn in enumerate(self.file_buttons):
            btn.grid(row=0, column=i, sticky="ew")  # Use ew for even distribution

        self.focus_file(new_button)

    def on_hover(self, event, button, color):
        """Changes button color on hover."""
        button.color = button["background"]
        button.config(bg=color)

    def on_leave(self, event, button):
        """Restores button color when not hovered."""
        button.config(bg=button.color)

    def clear_output(self):
        """Clears the output window."""
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete("1.0", tk.END)
        self.output_box.config(state=tk.DISABLED)
        self.write_to_output("output: ")

    def change_theme(self, name, button):
        """Changes the theme of the GUI."""
        # Use a dictionary for theme selection
        themes = {
            "light_theme": LightTheme(),
            "dark_theme": DarkTheme(),
            "default_theme": DefaultTheme()
        }
        self.theme = themes.get(name, DefaultTheme())  # Get theme or default

        # Update button styles
        for btn in self.theme_buttons:
            btn.config(font=default_fonts.setting_font)
        button.config(font=default_fonts.setting_selected_font)

        # You'll need to update colors of existing widgets here
        #... (e.g., self.main_frame.config(bg=self.theme.header_color))

    def create_menu_header(self, frame):
        """Creates the header menu with Import, Save, and Run buttons."""
        import_button = tk.Button(frame, text="Import", command=self.import_prog)
        import_button.place(relx=0, rely=0, relwidth=.05, relheight=1)
        self.style_button(import_button, type="menu")

        save_button = tk.Button(frame, text="Save", command=self.save_prog)
        save_button.place(relx=.05, rely=0, relwidth=.05, relheight=1)
        self.style_button(save_button, type="menu")

        new_file_button = tk.Button(frame, text="New", command=self.create_new_file)
        new_file_button.place(relx=.1, rely=0, relwidth=.05, relheight=1)
        self.style_button(new_file_button, type="menu")

        setting_button = tk.Button(frame, text="Settings", command=self.focus_setting_window)
        setting_button.place(relx=.15, rely=0, relwidth=.08, relheight=1)
        self.style_button(setting_button, type="menu")

        run_button = tk.Button(frame, text="Run", command=self.run_prog)
        run_button.place(relx=.23, rely=0, relwidth=.05, relheight=1)
        self.style_button(run_button, type="menu")

    def create_file_header(self, file_header):
        """Initializes the file header (currently empty)."""
        # This method can be expanded to add initial file buttons, etc.
        pass

    def create_editor(self, frame):
        """Creates the text editor with line numbers and scrollbar."""

        def on_scroll(*args):
            """Synchronizes scrolling between editor and line numbers."""
            self.text_editor.yview(*args)
            line_numbers.yview(*args)

        self.text_editor = tk.Text(
            frame,
            wrap=tk.WORD,
            font=default_fonts.editor_font,
            fg=self.theme.text_color,
            undo=True,
            bg=self.theme.editor_color,
            bd=0
        )

        line_numbers = tk.Text(
            frame,
            wrap=tk.WORD,
            font=default_fonts.line_num_font,
            fg=self.theme.text_color,
            width=4,
            padx=5,
            takefocus=0,
            state=tk.DISABLED,
            bg=self.theme.line_num_color,
            bd=0
        )

        scrollbar = tk.Scrollbar(frame, command=on_scroll)
        self.text_editor.config(yscrollcommand=scrollbar.set)
        line_numbers.config(yscrollcommand=scrollbar.set)

        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def update_line_numbers(event=None):
            """Updates the line number text box."""
            line_numbers.config(state=tk.NORMAL)
            line_numbers.delete("1.0", tk.END)
            line_count = self.text_editor.get("1.0", tk.END).count("\n")
            line_numbers.insert(tk.END, "\n".join(str(i) for i in range(1, line_count + 2)))  # Add 2 for initial line
            line_numbers.config(state=tk.DISABLED)

        self.text_editor.bind("<KeyPress>", update_line_numbers)
        self.text_editor.bind("<KeyRelease>", update_line_numbers)
        update_line_numbers()

    def create_output_window(self, frame):
        """Creates the output window with a scrollbar and input functionality."""
        self.output_box = tk.Text(
            frame,
            wrap=tk.WORD,
            fg=self.theme.text_color,
            font=default_fonts.output_font,
            bg=self.theme.output_color,
            bd=0
        )

        scrollbar = tk.Scrollbar(frame, command=self.output_box.yview)
        self.output_box.config(yscrollcommand=scrollbar.set)
        self.output_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initialize to the very beginning:
        self.input_start_index = "1.0"
        self.write_to_output("output:")

        # *Now* update to the correct position after "output:":
        self.input_start_index = self.output_box.index("insert")

        self.output_box.bind("<Return>", self.process_output_input)

        self.trash_img = tk.PhotoImage(file="trash.png")
        trash_button = tk.Button(
            self.output_box,
            image=self.trash_img,
            bg=self.theme.output_color,
            activebackground="grey",
            bd=0,
            command=self.clear_output
        )
        trash_button.place(relx=1.0, x=-30, rely=0.01)

    def process_output_input(self, event=None):
        """Processes user input from the output window."""
        print("process_output_input called")

        # Get input *starting from the stored index*
        input_value = self.output_box.get(self.input_start_index, tk.END).strip()
        print(f"Input value: '{input_value}'")
        if input_value:  # Only process if input is *not* empty
            GUI.output_queue.put(input_value)
            print("Input added to queue")
            self.output_box.edit_reset()  # <--- THE FIX!
            self.input_ready.set()
            print("input_ready set")
            self.input_start_index = self.output_box.index("insert")

    def wait_for_input_ready(self):
        """Waits for the input_ready event."""
        print("wait_for_input_ready called")  # Add this
        self.input_ready.wait()
        print("wait_for_input_ready finished waiting")  # Add this
        self.input_ready.clear()
        print("input_ready cleared")  # Add this

    def create_setting_header(self, frame):
        """Creates the header for the settings window."""
        save_n_exit_button = tk.Button(
            frame,
            text="Save & Exit",
            command=self.focus_main_window
        )
        save_n_exit_button.place(relx=0, rely=0, relwidth=.1, relheight=1)
        self.style_button(save_n_exit_button)

    def create_setting_window(self, frame):
        """Creates the content of the settings window."""
        setting_theme_frame = tk.Frame(frame, bg=self.theme.setting_content_color)
        setting_theme_frame.pack(side=tk.TOP, fill=tk.X)

        setting_theme_lbl = tk.Label(
            setting_theme_frame,
            text="Theme: ",
            font=('Helvatical bold', int(25)),
            bg=self.theme.setting_content_color,
            fg='black',
            pady=10
        )
        setting_theme_lbl.pack(side=tk.LEFT)

        # Store themes in a list for easier management
        self.theme_buttons = []
        theme_data = [
            ("default", "default_theme"),
            ("light", "light_theme"),
            ("dark", "dark_theme")
        ]

        for theme_name, theme_id in theme_data:
            theme_button = tk.Button(
                setting_theme_frame,
                text=theme_name,
                width=int(9),
                height=int(.5),
                pady=10,
                font=(default_fonts.setting_selected_font if self.theme.name == theme_id else default_fonts.setting_font)
            )
            theme_button.config(command=lambda t_id=theme_id, btn=theme_button: self.change_theme(t_id, btn))
            theme_button.pack(side=tk.RIGHT, padx=(5, 20))
            self.theme_buttons.append(theme_button)

def read_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            my_program = [int(line.strip().lstrip('+')) for line in lines]
            return my_program
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception:
        print(f"'{filename}' could not be read.")

def main():
    """Main function to initialize and run the Tkinter GUI."""
    root = tk.Tk()
    root.title('UVSim')
    root.geometry('900x600-0+0')

    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()