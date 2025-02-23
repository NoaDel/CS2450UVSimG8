import tkinter as tk
from tkinter import filedialog, scrolledtext

class UVSim:
    def __init__(self):
        self.memory = [0] * 100
        self.accumulator = 0
        self.instruction_counter = 0
        self.output_text = ""
        self.waiting_for_input = False  # Flag: Are we waiting for input?
        self.input_operand = None  # Store the operand for the input

    def load_program(self, program):
        for i, instruction in enumerate(program):
            self.memory[i] = instruction
        self.reset_output()
        self.waiting_for_input = False
        self.input_operand = None

    def reset_output(self):
        self.output_text = ""

    def append_output(self, text):
        self.output_text += str(text) + "\n"

    def get_output(self):
        return self.output_text

    def read(self, operand):
        # Instead of returning a function, we set state variables.
        self.waiting_for_input = True
        self.input_operand = operand
        self.append_output("Enter an integer:")

    def write(self, operand):
        self.append_output("Output: " + str(self.memory[operand]))

    def load(self, operand):
        self.accumulator = self.memory[operand]

    def store(self, operand):
        self.memory[operand] = self.accumulator

    def add(self, operand):
        self.accumulator += self.memory[operand]
        if not (-9999 <= self.accumulator <= 9999):
            self.append_output("Error: Overflow during addition.")
            return False
        return True

    def subtract(self, operand):
        self.accumulator -= self.memory[operand]
        if not (-9999 <= self.accumulator <= 9999):
            self.append_output("Error: Overflow during subtraction.")
            return False
        return True

    def divide(self, operand):
        if self.memory[operand] == 0:
            self.append_output("Error: Division by zero.")
            return False
        self.accumulator //= self.memory[operand]
        return True

    def multiply(self, operand):
        self.accumulator *= self.memory[operand]
        if not (-9999 <= self.accumulator <= 9999):
            self.append_output("Error: Overflow during multiplication.")
            return False
        return True

    def branch(self, operand):
        self.instruction_counter = operand

    def branchneg(self, operand):
        if self.accumulator < 0:
            self.instruction_counter = operand

    def branchzero(self, operand):
        if self.accumulator == 0:
            self.instruction_counter = operand

    def halt(self, operand):
        self.append_output("Program halted.")
        return False

    def execute_step(self, output_callback):
        """Executes a single step of the program."""
        if self.waiting_for_input:  # Don't execute if waiting for input
            return

        if self.instruction_counter >= len(self.memory) or self.instruction_counter < 0:
            self.append_output("Error: Instruction counter out of bounds.")
            return

        instruction = self.memory[self.instruction_counter]
        if not isinstance(instruction, int):
                instruction = 0
        opcode = instruction // 100
        operand = instruction % 100
        self.instruction_counter += 1

        if opcode == 10:
            self.read(operand)  # Set waiting_for_input and input_operand
            output_callback(self.get_output()) #show prompt
        elif opcode == 11:
            self.write(operand)
            output_callback(self.get_output())
        elif opcode == 20:
            self.load(operand)
        elif opcode == 21:
            self.store(operand)
        elif opcode == 30:
            if not self.add(operand):
                return
        elif opcode == 31:
            if not self.subtract(operand):
                return
        elif opcode == 32:
            if not self.divide(operand):
                return
        elif opcode == 33:
            if not self.multiply(operand):
                return
        elif opcode == 40:
            self.branch(operand)
        elif opcode == 41:
            self.branchneg(operand)
        elif opcode == 42:
            self.branchzero(operand)
        elif opcode == 43:
            if self.halt(operand) is False:
                return
            output_callback(self.get_output())
        else:
            self.append_output("Error: Invalid opcode.")
            return

        if not -9999 <= self.accumulator <= 9999:
            self.append_output("Error: Accumulator overflow.")
            return

    def provide_input(self, value):
        """Provides input to the simulator."""
        try:
            value = int(value)
            if -9999 <= value <= 9999:
                self.memory[self.input_operand] = value
                self.waiting_for_input = False  # No longer waiting
                self.input_operand = None      # Clear operand
            else:
                self.append_output("Error: Input out of range (-9999 to 9999).")
                # Don't clear waiting_for_input, still need valid input
        except ValueError:
            self.append_output("Error: Invalid input. Please enter an integer.")
            # Don't clear waiting_for_input, still need valid input


class UVSimApp:
    def __init__(self, master):
        self.master = master
        master.title("UVSim Simulator")

        self.simulator = UVSim()

        self.top_frame = tk.Frame(master)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.import_button = tk.Button(self.top_frame, text="Import", command=self.import_file)
        self.import_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.top_frame, text="Save", command=self.save_file)
        self.save_button.pack(side=tk.LEFT)

        self.new_button = tk.Button(self.top_frame, text="New", command=self.new_file)
        self.new_button.pack(side=tk.LEFT)

        self.run_button = tk.Button(self.top_frame, text="Run", command=self.run_program)
        self.run_button.pack(side=tk.LEFT)

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.program_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD)
        self.program_text.pack(fill=tk.BOTH, expand=True)

        self.console_frame = tk.Frame(master)
        self.console_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.console_text = scrolledtext.ScrolledText(self.console_frame, wrap=tk.WORD, state='disabled')
        self.console_text.pack(fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(self.console_frame)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_button = tk.Button(self.input_frame, text="Enter", command=self.process_input)
        self.input_button.pack(side=tk.LEFT)
        self.input_button.config(state="disabled")

    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.program_text.delete('1.0', tk.END)
                self.program_text.insert('1.0', file.read())

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.program_text.get('1.0', tk.END))

    def new_file(self):
        self.program_text.delete('1.0', tk.END)

    def run_program(self):
        program_string = self.program_text.get('1.0', tk.END)
        try:
            program = [int(line.strip()) for line in program_string.splitlines() if line.strip()]
            self.simulator.load_program(program)
            self.input_button.config(state="disabled")  # Disable initially
            self.continue_execution()  # Start the execution loop
        except ValueError:
            self.display_error("Invalid program format.")
        except Exception as e:
            self.display_error(f"An error occurred: {e}")

    def continue_execution(self):
        """Continues execution until input is needed or the program halts."""
        while not self.simulator.waiting_for_input:
            self.simulator.execute_step(self.update_console)
            if self.simulator.instruction_counter == len(self.simulator.memory): #halt instruction/end of program
                break
        if self.simulator.waiting_for_input:
            self.input_button.config(state="normal")  # Enable input if needed
        else:
            self.input_button.config(state="disabled") #program completed

    def process_input(self):
        user_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.simulator.provide_input(user_input)
        self.update_console(self.simulator.get_output())  # Update after input
        self.continue_execution()  # Continue after providing input


    def update_console(self, text):
        self.console_text.config(state='normal')
        self.console_text.insert(tk.END, text)
        self.console_text.config(state='disabled')
        self.console_text.see(tk.END)

    def display_error(self, message):
        self.update_console("ERROR: " + message)

root = tk.Tk()
app = UVSimApp(root)
root.mainloop()