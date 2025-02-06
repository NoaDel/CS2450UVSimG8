class UVSim:
    
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

