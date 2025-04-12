# UVSim Program
Information and updates about the UVSim program can be found here.

### Team Members
  * Caden Brooks
  * Jacob Bunker
  * Noah Delano
  * Landon Towers

Our program was written and tested in Python 3.

## 1. What is UVSim?

The "Sim" in our name stands for simulator, and our program simulates machine code execution. Users can submit text files with machine code instructions using BasicML operations. Below is a list of possible BasicML commands:

#### I/O operations:
  * READ = 10  
    Read a word from the keyboard into a specific location in memory.
  * WRITE = 11  
    Write a word from a specific location in memory to the screen.

#### Load/store operations:
  * LOAD = 20  
    Load a word from a specific location in memory into the accumulator.
  * STORE = 21  
    Store a word from the accumulator into a specific location in memory.

#### Arithmetic operations:
  * ADD = 30  
    Add a word from a specific location in memory to the word in the accumulator.
  * SUBTRACT = 31  
    Subtract a word from a specific location in memory from the word in the accumulator.
  * DIVIDE = 32  
    Divide the word in the accumulator by a word from a specific location in memory.
  * MULTIPLY = 33  
    Multiply a word from a specific location in memory by the word in the accumulator.

#### Control operations:
  * BRANCH = 40  
    Branch to a specific location in memory.
  * BRANCHNEG = 41  
    Branch to a specific location in memory if the accumulator is negative.
  * BRANCHZERO = 42  
    Branch to a specific location in memory if the accumulator is zero.
  * HALT = 43  
    Pause the program.

Using these operations, users can simulate their own machine code!

## 2. How to run UVSim via Terminal

Users will need to install Python 3 on their local machine to run UVSim.

Machine code instructions should be saved in a text file, where each instruction:
  * Begins with a "+" sign followed by four digits (e.g., +1095).
  * Ends with a newline.
  * May include comments using /* ... */.

Example program (reads two integers and outputs their sum):
