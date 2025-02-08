import sys

class UVSim:
    def __init__(self):
        self.memory = [0] * 100
        self.accumulator = 0
        self.instruction_counter = 0

    def load_program(self, program):
        for i, instruction in enumerate(program):
            self.memory[i] = instruction
    
    # I/O Operations
    def read(self, operand):
        try:
            value = int(input("Enter an integer: "))
            if -9999 <= value <= 9999:
                self.memory[operand] = value
            else:
                print("Error: Input out of range (-9999 to 9999).")
                self.instruction_counter -= 1  # Re-execute
        except ValueError:
            print("Error: Invalid input. Please enter an integer.")
            if (self.instruction_counter > 0):
                self.instruction_counter -= 1  # Re-execute

    def write(self, operand):
        print("Output:", self.memory[operand])

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
            instruction = self.memory[self.instruction_counter]
            opcode = instruction // 100
            operand = instruction % 100

            self.instruction_counter += 1

            # Execute the appropriate function based on the opcode
            if opcode == 10:
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

            # Check for accumulator overflow after potential overflow operations
            if not -9999 <= self.accumulator <= 9999:
                print("Error: Accumulator overflow.")
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
