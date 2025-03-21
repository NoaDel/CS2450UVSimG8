import sys
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
        print(self.memory)
        while True:
            try:
                instruction = self.memory[self.instruction_counter]
                # .rstrip('\n').lstrip('+')
                print(instruction)
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
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()  # Reads all lines into a list
            # print(lines)
            my_program = [int(line.strip().lstrip('+')) for line in lines]
            # print(my_program)
            return my_program
            # You can further process 'values' as needed
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception:
        print(f"'{filename}' could not be read.")

if __name__ == "__main__":
    simulator = UVSim()
    input_file = sys.argv[1]
    program = read_file(input_file)

    simulator.load_program(program)
    simulator.execute_program()
