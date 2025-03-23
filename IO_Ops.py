from output_handler import OutputHandler

# I/O Operations
class IO:
    def read(memory, instruction_counter, operand):
        # value = int(input("Enter an integer: ")) #Commenting this allows GUI to continue.
        # value = OutputHandler.get_int_input()
        if not OutputHandler.via_terminal:
            print('before')
            value = OutputHandler.input_vals.pop(0)
            print('after')
            if -9999 <= value <= 9999:
                memory[operand] = value
            else:
                OutputHandler.write_to_output("ERROR: Input out of accepting range -9999 to 9999. Program halted.")
                print("Error: Input out of range (-9999 to 9999).")
                while memory[instruction_counter] != '0':
                    instruction_counter += 1  # Re-execute
                instruction_counter -= 1
        else:
            while True:
                try:
                    value = int(input("Enter an integer: "))
                    if -9999 <= value <= 9999:
                        memory[operand] = value
                        break
                    else:
                        print("Error: Input out of range (-9999 to 9999).")
                except:
                    print("Error: Invalid input type.")

        # Request integer input asynchronously
        return instruction_counter

    def write(memory, operand):
        OutputHandler.write_to_output(f"Output: {memory[operand]}")
        print("Output:", memory[operand])

    # Load/Store Operations
    def load(memory, operand):
        return memory[operand]

    def store(accum):
        return accum
