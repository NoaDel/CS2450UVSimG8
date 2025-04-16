# UVSim Program
Information and updates about the UVSim program can be found here.
### Team Members
  * Caden Brooks
  * Jacob Bunker
  * Noah Delano
  * Landon Towers

Our program was written and tested in Python 3.

## 1. What is UVSim?

Fantastic question! We're glad you asked! The Sim in our name stands for simulator, and our program simulates machine code execution. Users will be able to submit text files with machine code instructions through BasicML operations. Below is a list of possible BasicML commands:

  #### I/O operations:
  * READ = 10 Read a word from the keyboard into a specific location in memory.
  * WRITE = 11 Write a word from a specific location in memory to screen.

  #### Load/store operations:
  * LOAD = 20 Load a word from a specific location in memory into the accumulator.
  * STORE = 21 Store a word from the accumulator into a specific location in memory.
  
  #### Arithmetic operations:
  * ADD = 30 Add a word from a specific location in memory to the word in the accumulator (leave the result in the accumulator)
  * SUBTRACT = 31 Subtract a word from a specific location in memory from the word in the accumulator (leave the result in the accumulator)
  * DIVIDE = 32 Divide the word in the accumulator by a word from a specific location in memory (leave the result in the accumulator).
  * MULTIPLY = 33 multiply a word from a specific location in memory to the word in the accumulator (leave the result in the accumulator).
  
  #### Control operations:
  * BRANCH = 40 Branch to a specific location in memory
  * BRANCHNEG = 41 Branch to a specific location in memory if the accumulator is negative.
  * BRANCHZERO = 42 Branch to a specific location in memory if the accumulator is zero.
  * HALT = 43 Pause the program

Using these operations, users should be able to simulate their own machine code!

## 2. How to run UVSim via Terminal

Users will need to install Python 3 on their local machine to run UVSim.

Machine code instructions should be in a text file, and each instruction must begin with a plus sign to represent the start of the instruction, and end with a newline. To add comments, use /* at the beginning and */ to close the comment.

Here is one example of an instruction set that reads two integers and outputs the sum:

```
+1095  /* READ A */
+1096  /* READ B */
+2095  /* LOAD A */
+3096  /* ADD B */
+2197  /* STORE RESULT */
+1197  /* WRITE RESULT */
+4300  /* HALT */
```

To run UVSim on the command line, use this command, replacing the last argument with the name of the text file being used:

```
python3 UVSim.py {.txt file}
```

## 3. How to run UVSim via GUI

Users will need to install Python 3 on their local machine to run UVSim.

To run UVSim on the GUI, use this command:

```
python3 GUI_code.py
```

Machine code instructions can be placed in the GUI editor. To add comments, use /* at the beginning and */ to close the comment. If the read operation is being used (opcode 10), include your inputs in the input box on the right hand side before running the program. 

Use the navigation menu as needed to import, save, or make new files. Click on settings to change the theme, and run to run your program!

Thanks for giving UVSim a try!
Last updated Mar. 22, 2025
