from output_handler import OutputHandler
# Control Operations
def branchpos(counter, accum, operand):
    if accum > 0:
        counter = operand
    return counter

def branchneg(counter, accum, operand):
    if accum < 0:
        counter = operand
    return counter

def branchzero(counter, accum, operand):
    if accum == 0:
        counter = operand
    return counter

def halt():
    OutputHandler.write_to_output("Program halted.")
    print("Program halted.")
