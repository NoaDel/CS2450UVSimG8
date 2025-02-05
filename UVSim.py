class UVSim:
    def __init__(self):
        self.memory = [0] * 100
        self.accumulator = 0
        self.instruction_counter = 0

    def load_program(self, program):
        for i, instruction in enumerate(program):
            self.memory[i] = instruction

    def execute_program(self):
        while True:
            instruction = self.memory[self.instruction_counter]
            opcode = instruction // 100
            operand = instruction % 100

            self.instruction_counter += 1

            # Execute the appropriate function based on the opcode
            if opcode == 10:
                break;
            elif opcode == 11:
                break;
            elif opcode == 20:
                break;
            elif opcode == 21:
                break;
            elif opcode == 30:
                break;
            elif opcode == 31:
                break;
            elif opcode == 32:
                break;
            elif opcode == 33:
                break;
            elif opcode == 40:
                break;
            elif opcode == 41:
                break;
            elif opcode == 42:
                break;
            elif opcode == 43:
                break;
            else:
                break;

            # Check for accumulator overflow after potential overflow operations
            if not -9999 <= self.accumulator <= 9999:
                print("Error: Accumulator overflow.")
                return


if __name__ == "__main__":
    simulator = UVSim()

    program = [
        1095,  # READ A
        1096,  # READ B
        2095,  # LOAD A
        3096,  # ADD B
        2197,  # STORE RESULT
        1197,  # WRITE RESULT
        4300,  # HALT
    ]

    simulator.load_program(program)
    simulator.execute_program()