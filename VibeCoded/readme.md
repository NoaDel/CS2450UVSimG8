# UVSim IDE - BasicML Simulator

## Overview

This application is a graphical Integrated Development Environment (IDE) for the **UVSim**, a virtual computer simulator. It allows you to write, load, save, and execute programs written in **BasicML (Basic Machine Language)**.

This version of the UVSim operates exclusively in **6-digit mode**, meaning memory words and instructions use a sign followed by 6 digits (e.g., `+100005`, `-000123`). It supports a memory space of 250 words (addresses 000-249) and data values ranging from -999999 to +999999.

The IDE also includes a feature to detect and optionally convert legacy 4-digit BasicML files to the standard 6-digit format upon opening.

## Features

* **Code Editor:** A simple text editor with line numbers for writing 6-digit BasicML code.
* **Tabbed Interface:** Open and work with multiple BasicML files simultaneously.
* **File Operations:** Create new files, open existing files (`.bml`, `.txt`), save, and save-as.
* **4-Digit File Conversion:** Automatically detects legacy 4-digit BasicML files and prompts the user to convert them to 6-digit format, saving the result as a new file.
* **Execution Control:** Run the BasicML program in the active tab and reset the simulator state.
* **State Display:** View the current values of the **Accumulator** and **Program Counter (PC)**.
* **Memory Viewer:** Open a separate window to inspect the contents of all 250 memory locations.
* **Input/Output Panel:** Displays output from the running program (via the `WRITE` instruction) and shows prompts for user input (via the `READ` instruction).
* **Theming:** Switch between a UVU-themed (Green/White) and a Dark theme.

## Prerequisites

* **Python 3:** Ensure you have Python 3 installed (version 3.6 or later recommended).
* **Tkinter:** This GUI library is usually included with standard Python installations. If not, you may need to install it separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu, or it might be included in the Python installer on Windows/macOS).

## How to Use

1.  **Run the IDE:**
    * Navigate to the directory containing the project files in your terminal.
    * Run the command: `python3 uvsim_gui.py`

2.  **Writing BasicML Code:**
    * Use the editor pane to write your program.
    * Each line should contain one 6-digit BasicML word, preceded by a sign (`+` or `-`).
    * Format:
        * **Instructions:** `+OooAaa` (e.g., `+10005` for READ into address 005)
        * **Positive Data:** `+DDDDDD` (e.g., `+000123`)
        * **Negative Data:** `-DDDDDD` (e.g., `-000045`)
    * Lines starting with `#` are comments and are ignored.
    * Empty lines are ignored.
    * The program is loaded into memory starting from address 000. The maximum program size is 250 words.

3.  **BasicML Opcodes (6-Digit):**

    | Opcode | Name         | Description                                      |
    | :----- | :----------- | :----------------------------------------------- |
    | `10`   | `READ`       | Read an integer from user into memory location.  |
    | `11`   | `WRITE`      | Write the value from memory location to output.  |
    | `20`   | `LOAD`       | Load value from memory location into Accumulator. |
    | `21`   | `STORE`      | Store value from Accumulator into memory location.|
    | `30`   | `ADD`        | Add value from memory location to Accumulator.   |
    | `31`   | `SUBTRACT`   | Subtract value from memory location from Accumulator.|
    | `32`   | `DIVIDE`     | Divide Accumulator by value from memory location (integer division). |
    | `33`   | `MULTIPLY`   | Multiply Accumulator by value from memory location.|
    | `40`   | `BRANCH`     | Branch to memory location unconditionally.       |
    | `41`   | `BRANCHNEG`  | Branch if Accumulator is negative.             |
    | `42`   | `BRANCHZERO` | Branch if Accumulator is zero.                 |
    | `43`   | `HALT`       | Halt program execution.                          |

    * `Aaa` in instructions refers to a 3-digit memory address (000-249).

4.  **Loading and Saving:**
    * Use **File -> New** or the "New" button to create an empty tab.
    * Use **File -> Open...** or the "Open" button to load a `.bml` or `.txt` file.
        * If a 4-digit file is detected, you'll be asked if you want to convert and save it as a new 6-digit file (e.g., `original (ported).bml`).
    * Use **File -> Save** / **Save As...** or the "Save" button to save your code. Unsaved tabs will have an asterisk (`*`) next to their name.

5.  **Running and Resetting:**
    * Click the **Run** button or use **Run -> Run Program** (F5) to execute the code in the currently active tab.
        * The simulator will load the code from the editor into memory.
        * Output appears in the "Input/Output Panel".
        * If a `READ` instruction is encountered, a dialog box will pop up asking for input.
        * Execution stops on `HALT` or if an error occurs (e.g., division by zero, invalid memory access, overflow).
    * Click the **Reset** button or use **Run -> Reset Simulator** to clear the simulator's memory, accumulator, and program counter for the active tab. This does *not* clear the editor content.

6.  **Viewing Memory:**
    * Click the **View Memory** button in the state display area or use **View -> View Memory**.
    * This opens a window showing the contents of all 250 memory locations for the simulator associated with the currently active tab.
    * Use the "Refresh" button in the memory view window to update it if the program is running or after reset/load.

## Project File Structure

* `uvsim_gui.py`: The main application file, runs the IDE.
* `uvsim_core_logic.py`: Contains the `UVSim` class implementing the virtual machine logic.
* `uvsim_editor_tab.py`: Defines the `EditorTab` class managing the editor, line numbers, and scrollbars within a tab.
* `uvsim_file_handler.py`: Contains functions for file dialogs and reading/writing files.
* `uvsim_theme_manager.py`: Manages theme definitions and application of styles.
* `uvsim_tests.py`: Unit tests for the core logic and porting functions.

