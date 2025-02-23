from output_handler import OutputHandler
# Arithmetic Operations
def add(accum, memory, operand):
    accum += memory[operand]
    if not (-9999 <= accum <= 9999):
        OutputHandler.write_to_output("Error: Overflow during addition.")
        print("Error: Overflow during addition.")
        return (False, accum)
    # print(accum)
    return (True, accum)

def subtract(accum, memory, operand):
    accum -= memory[operand]
    if not (-9999 <= accum <= 9999):
        OutputHandler.write_to_output("Error: Overflow during subtraction.")
        print("Error: Overflow during subtraction.")
        return (False, accum)
    return (True, accum)

def divide(accum, memory, operand):
    if memory[operand] == 0:
        OutputHandler.write_to_output("Error: Division by zero.")
        print("Error: Division by zero.")
        return (False, accum)
    accum //= memory[operand]
    return (True, accum)

def multiply(accum, memory, operand):
    accum *= memory[operand]
    if not (-9999 <= accum <= 9999):
        OutputHandler.write_to_output("Error: Overflow during multiplication.")
        print("Error: Overflow during multiplication.")
        return (False, accum)
    return (True, accum)
