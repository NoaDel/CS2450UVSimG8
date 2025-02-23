from output_handler import OutputHandler
import asyncio
import concurrent.futures
# I/O Operations
class IO:
    def read(memory, instruction_counter, operand):
        # value = int(input("Enter an integer: ")) #Commenting this allows GUI to continue.
        # value = OutputHandler.get_int_input()
        value = OutputHandler.input_vals.pop(0)
        
        if -9999 <= value <= 9999:
            memory[operand] = value
        else:
            OutputHandler.write_to_output("Error: Input out of range (-9999 to 9999).")
            print("Error: Input out of range (-9999 to 9999).")
            instruction_counter -= 1  # Re-execute

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
