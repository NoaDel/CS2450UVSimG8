import sys
import re
from IO_Ops import IO
import ArithOps, ControlOps
from output_handler import OutputHandler

class UVSim:
    def __init__(self):
        self.memory = [0] * 100
        self.accumulator = 0
        self.instruction_counter = 0

    def load_program(self, program):
        for i, instruction in enumerate(program):
            self.memory[i] = instruction

    def execute_program(self):
        # print(self.memory)
        while True:
            try:
                instruction = self.memory[self.instruction_counter]
                # .rstrip('\n').lstrip('+')
                # print(instruction)
                opcode = instruction // 100
                operand = instruction % 100

                self.instruction_counter += 1

                # Execute the appropriate function based on the opcode
                if opcode == 10:
                    self.instruction_counter = IO.read(self.memory, self.instruction_counter, operand)
                elif opcode == 11:
                    IO.write(self.memory, operand)
                elif opcode == 20:
                    self.accumulator = IO.load(self.memory, operand)
                elif opcode == 21:
                    self.memory[operand] = IO.store(self.accumulator)
                elif opcode == 30:
                    add_results = ArithOps.add(self.accumulator, self.memory, operand)
                    if not add_results[0]: #First parameter of returned tuple check bool value
                        break
                    self.accumulator = add_results[1] #If adding success, put second parameter of returned tuple in accumulator
                elif opcode == 31:
                    sub_results = ArithOps.subtract(self.accumulator, self.memory, operand)
                    if not sub_results[0]:
                        break
                    self.accumulator = sub_results[1]
                elif opcode == 32:
                    div_results = ArithOps.divide(self.accumulator, self.memory, operand)
                    if not div_results[0]:
                        break
                    self.accumulator = div_results[1]
                elif opcode == 33:
                    mult_results = ArithOps.multiply(self.accumulator, self.memory, operand)
                    if not mult_results[0]:
                        break
                    self.accumulator = mult_results[1]
                elif opcode == 40:
                    self.instruction_counter = ControlOps.branchpos(self.instruction_counter, self.accumulator, operand)
                elif opcode == 41:
                    self.instruction_counter = ControlOps.branchneg(self.instruction_counter, self.accumulator, operand)
                elif opcode == 42:
                    self.instruction_counter = ControlOps.branchzero(self.instruction_counter, self.accumulator, operand)
                elif opcode == 43:
                    ControlOps.halt()
                    break
                else:
                    print("Error: Invalid opcode.")
                    OutputHandler.write_to_output("ERROR: Invalid opcode detected. Program halted.")
                    ControlOps.halt()
                    break
            except:
                # print("Try block failed")
                break

            # Check for accumulator overflow after potential overflow operations
            if not -9999 <= self.accumulator <= 9999:
                print("Error: Accumulator overflow.")
                OutputHandler.write_to_output("ERROR: Accumulator overflow.")
                return

def read_file(filename):
    cleaned_lines = clean_program_file(filename)
    try:
        my_program = [int(line) for line in cleaned_lines]
        return my_program
    except ValueError as e:
        print(f"Error: Non-integer value found in cleaned file. {e}")
        return []

def clean_program_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # remove all + signs
        content = content.replace('+', '')

        # remove excessive newlines
        lines = [line.strip() for line in content.splitlines()]
        # remove empty lines
        lines = [line for line in lines if line]
        return lines
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []
    except Exception as e:
        print(f"'{filename}' could not be processed. Error: {e}")
        return []

if __name__ == "__main__":
    simulator = UVSim()
    input_file = sys.argv[1]
    program = read_file(input_file)

    if len(program) > 100:
        print("ERROR: Program is too long (100 command limit)\n")
    # print(program) #Confirms program is correctly set into the array
    else:
        print("Running program...")
        OutputHandler.via_terminal = True
        simulator.load_program(program) #The reason for inputting 1: is because the first instruction is always invalid
        simulator.execute_program()
        print('\n')
        OutputHandler.via_terminal = False #Resets
