import sys

class UVSim:
    """
    Simulates the UVSim virtual computer architecture.

    Operates EXCLUSIVELY in 6-digit mode (250 words, +/-999999 range).
    Provides helper functions for format detection and 4-to-6 digit porting.
    """

    # Constants for opcodes (now only 3-digit are relevant internally)
    READ = 10; WRITE = 11; LOAD = 20; STORE = 21; ADD = 30; SUBTRACT = 31
    DIVIDE = 32; MULTIPLY = 33; BRANCH = 40; BRANCHNEG = 41; BRANCHZERO = 42; HALT = 43

    # --- Constants for 6-digit operation ---
    WORD_LENGTH = 6; MAX_MEMORY_ADDRESS = 249
    MAX_WORD_VALUE = 999999; MIN_WORD_VALUE = -999999
    PC_FORMAT = "{:03d}"; OPERAND_FORMAT = "{:03d}"
    MEM_RANGE_DISPLAY = f"000-{MAX_MEMORY_ADDRESS}"

    # Opcode map for porting 4-digit to 6-digit instructions
    OPCODE_4_TO_6_MAP = {
        10: READ, 11: WRITE, 20: LOAD, 21: STORE, 30: ADD, 31: SUBTRACT,
        32: DIVIDE, 33: MULTIPLY, 40: BRANCH, 41: BRANCHNEG, 42: BRANCHZERO,
        43: HALT
    }

    def __init__(self, io_read_func=None, io_write_func=None):
        """Initializes the UVSim simulator (always in 6-digit mode)."""
        self.memory = {}
        self.accumulator = 0
        self.program_counter = 0
        self.is_running = False
        self.io_read = io_read_func if io_read_func else self._default_read
        self.io_write = io_write_func if io_write_func else self._default_write

        # --- Refactored Opcode Dispatch ---
        # Map opcodes to their corresponding execution methods
        self._opcode_dispatch = {
            self.READ: self._execute_read,
            self.WRITE: self._execute_write,
            self.LOAD: self._execute_load,
            self.STORE: self._execute_store,
            self.ADD: self._execute_add,
            self.SUBTRACT: self._execute_subtract,
            self.DIVIDE: self._execute_divide,
            self.MULTIPLY: self._execute_multiply,
            self.BRANCH: self._execute_branch,
            self.BRANCHNEG: self._execute_branchneg,
            self.BRANCHZERO: self._execute_branchzero,
            self.HALT: self._execute_halt,
        }
        self.reset()

    def _default_read(self):
        """Default READ operation using standard input."""
        while True:
            try:
                prompt = f"Enter an integer ({self.MIN_WORD_VALUE} to {self.MAX_WORD_VALUE}): "
                value_str = input(prompt)
                value = int(value_str)
                if not (self.MIN_WORD_VALUE <= value <= self.MAX_WORD_VALUE):
                    raise ValueError(f"Input must be between {self.MIN_WORD_VALUE} and {self.MAX_WORD_VALUE}.")
                return value
            except ValueError as e:
                print(f"Invalid input: {e}. Please try again.", file=sys.stderr)
            except EOFError:
                 print("\nInput stream closed unexpectedly.", file=sys.stderr)
                 raise # Re-raise EOFError to signal halt

    def _default_write(self, value):
        """Default WRITE operation using standard output (prints integer)."""
        print(f"Output: {value}")

    def _format_word(self, value):
        """Formats a number as a signed 6-digit word."""
        # Ensure value is treated as an integer before formatting
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            # Handle cases where value might not be easily convertible to int
            # For simplicity, return a default error format or raise an error
            # Here, we'll return a placeholder indicating an issue.
            return "+ERR000" # Or consider raising a specific internal error

        sign = '+' if int_value >= 0 else '-'
        # Use the defined WORD_LENGTH for formatting
        return f"{sign}{abs(int_value):0{self.WORD_LENGTH}d}"


    def reset(self):
        """Resets the accumulator, program counter, and clears memory."""
        self.memory = {i: 0 for i in range(self.MAX_MEMORY_ADDRESS + 1)}
        self.accumulator = 0
        self.program_counter = 0
        self.is_running = False

    @staticmethod
    def detect_format(program_lines):
        """
        Detects the word format (4 or 6 digits) from program lines.

        Args:
            program_lines (list[str]): A list of strings, each representing a line of code.

        Returns:
            int: The detected word length (4 or 6).

        Raises:
            ValueError: If the format is invalid, inconsistent, or cannot be determined.
        """
        detected_length = None
        has_code = False
        for i, line in enumerate(program_lines):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            has_code = True

            # Basic format check: must start with '+' or '-'
            if not (line.startswith('+') or line.startswith('-')):
                raise ValueError(f"Line {i+1}: Invalid format - Must start with '+' or '-'. Found: '{line}'")

            # Check length of the numeric part
            num_part_len = len(line) - 1
            if num_part_len not in [4, 6]:
                raise ValueError(f"Line {i+1}: Invalid word length - Must be 4 or 6 digits after sign. Found: '{line}'")

            # Detect format based on the first valid code line
            if detected_length is None:
                detected_length = num_part_len
            # Ensure consistency across lines
            elif detected_length != num_part_len:
                raise ValueError(f"Line {i+1}: Mixed format detected - Expected {detected_length}-digit words, found {num_part_len}-digit word: '{line}'")

            # Check if the numeric part is actually a number
            try:
                int(line) # Check if the whole line (including sign) is a valid integer
            except ValueError:
                raise ValueError(f"Line {i+1}: Invalid number format. Found: '{line}'")

        # If no code lines were found, default to 6-digit format (or raise error if preferred)
        if not has_code:
            # print("Warning: No code found, defaulting to 6-digit format.", file=sys.stderr)
            return 6 # Default assumption if no code lines

        # If code was found but format couldn't be determined (shouldn't happen with current logic)
        if detected_length is None:
             raise ValueError("Could not determine format despite finding lines.") # Should be unreachable

        return detected_length

    def load_program_from_lines(self, program_lines):
        """
        Loads a 6-DIGIT BasicML program into memory from a list of strings.

        Args:
            program_lines (list[str]): List of strings containing 6-digit code.

        Returns:
            bool: True if loading was successful.

        Raises:
            ValueError: If the program contains invalid format, exceeds memory limits,
                        or has values out of the 6-digit range.
        """
        self.reset()
        line_count = 0
        for i, line in enumerate(program_lines):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue

            # Check memory bounds before attempting to load
            if line_count > self.MAX_MEMORY_ADDRESS:
                raise ValueError(f"Program exceeds memory limit of {self.MAX_MEMORY_ADDRESS + 1} words at line {i+1}.")

            try:
                # --- Strict 6-digit Format Validation ---
                # 1. Check total length (sign + 6 digits)
                if len(line) != self.WORD_LENGTH + 1:
                    raise ValueError(f"Expected {self.WORD_LENGTH + 1} characters (sign + {self.WORD_LENGTH} digits). Found: '{line}'")

                # 2. Check for valid sign
                if line[0] not in '+-':
                     raise ValueError(f"Word must start with '+' or '-'. Found: '{line}'")

                # 3. Attempt conversion to integer
                value = int(line) # This implicitly checks if digits are valid

                # 4. Check if value is within the allowed 6-digit range
                if not (self.MIN_WORD_VALUE <= value <= self.MAX_WORD_VALUE):
                    raise ValueError(f"Value {value} out of 6-digit range ({self.MIN_WORD_VALUE} to {self.MAX_WORD_VALUE}).")

                # 5. Redundant check (already covered by int() conversion), but keeps original intent
                # if value >= 0 and line[0] != '+':
                #    raise ValueError(f"Positive words must start with '+'. Found: '{line}'.")
                # if value < 0 and line[0] != '-':
                #    raise ValueError(f"Negative words must start with '-'. Found: '{line}'.")

                # Load into memory
                self.memory[line_count] = value
                line_count += 1

            except ValueError as e:
                # Add line number context if not already present
                msg = str(e)
                if f"line {i+1}" not in msg.lower():
                    raise ValueError(f"Line {i+1}: Invalid 6-digit word format or value '{line}'. Original error: {e}")
                else:
                    raise # Re-raise the exception with existing line context

        # print(f"Successfully loaded {line_count} words into memory.")
        return True # Indicate successful loading

    def get_memory_value(self, address):
        """
        Safely gets a value from memory.

        Args:
            address (int): The memory address to read from.

        Returns:
            int: The value at the specified memory address.

        Raises:
            ValueError: If the address is out of bounds.
        """
        if not (0 <= address <= self.MAX_MEMORY_ADDRESS):
            raise ValueError(f"Memory address {self.PC_FORMAT.format(address)} out of bounds ({self.MEM_RANGE_DISPLAY}).")
        # Return the value or 0 if the address somehow wasn't initialized (shouldn't happen with reset)
        return self.memory.get(address, 0)

    def _check_overflow(self, value):
        """
        Checks if a value exceeds the 6-digit word limits.

        Args:
            value (int): The value to check.

        Returns:
            int: The value if it's within limits.

        Raises:
            OverflowError: If the value is outside the 6-digit range.
        """
        if not (self.MIN_WORD_VALUE <= value <= self.MAX_WORD_VALUE):
            raise OverflowError(f"Arithmetic overflow/underflow: {value} is outside the 6-digit range [{self.MIN_WORD_VALUE}, {self.MAX_WORD_VALUE}].")
        return value

    # --- Opcode Execution Methods ---

    def _execute_read(self, operand):
        """Executes the READ operation."""
        value = self.io_read() # Calls the configured read function
        self.memory[operand] = self._check_overflow(value)
        return self.program_counter + 1, False # next_pc, halt_execution

    def _execute_write(self, operand):
        """Executes the WRITE operation."""
        value = self.get_memory_value(operand)
        self.io_write(value) # Calls the configured write function
        return self.program_counter + 1, False

    def _execute_load(self, operand):
        """Executes the LOAD operation."""
        self.accumulator = self.get_memory_value(operand)
        return self.program_counter + 1, False

    def _execute_store(self, operand):
        """Executes the STORE operation."""
        # Store the *current* accumulator value, checking for overflow is implicit
        # as the accumulator should always hold a valid value after other ops.
        self.memory[operand] = self.accumulator
        return self.program_counter + 1, False

    def _execute_add(self, operand):
        """Executes the ADD operation."""
        value = self.get_memory_value(operand)
        result = self.accumulator + value
        self.accumulator = self._check_overflow(result)
        return self.program_counter + 1, False

    def _execute_subtract(self, operand):
        """Executes the SUBTRACT operation."""
        value = self.get_memory_value(operand)
        result = self.accumulator - value
        self.accumulator = self._check_overflow(result)
        return self.program_counter + 1, False

    def _execute_divide(self, operand):
        """Executes the DIVIDE operation."""
        value = self.get_memory_value(operand)
        if value == 0:
            raise ZeroDivisionError(f"Division by zero at address {self.PC_FORMAT.format(self.program_counter)}.")
        # Use integer division, result truncated towards zero
        result = int(self.accumulator / value)
        self.accumulator = self._check_overflow(result) # Check overflow on the result
        return self.program_counter + 1, False

    def _execute_multiply(self, operand):
        """Executes the MULTIPLY operation."""
        value = self.get_memory_value(operand)
        result = self.accumulator * value
        self.accumulator = self._check_overflow(result)
        return self.program_counter + 1, False

    def _execute_branch(self, operand):
        """Executes the BRANCH operation."""
        return operand, False # next_pc is the operand

    def _execute_branchneg(self, operand):
        """Executes the BRANCHNEG operation."""
        if self.accumulator < 0:
            return operand, False # Branch taken
        else:
            return self.program_counter + 1, False # Branch not taken

    def _execute_branchzero(self, operand):
        """Executes the BRANCHZERO operation."""
        if self.accumulator == 0:
            return operand, False # Branch taken
        else:
            return self.program_counter + 1, False # Branch not taken

    def _execute_halt(self, operand):
        """Executes the HALT operation."""
        # Operand is ignored for HALT
        return self.program_counter, True # next_pc doesn't matter, halt_execution is True

    # --- Main Execution Logic ---

    def step(self):
        """
        Executes a single 6-digit instruction using opcode dispatch.

        Returns:
            bool: True if execution should continue, False if HALT was executed or an error occurred.

        Raises:
            RuntimeError: If the Program Counter is out of bounds.
            ValueError: If an invalid instruction format, opcode, or operand address is encountered.
            ZeroDivisionError: If division by zero is attempted.
            OverflowError: If an arithmetic operation results in overflow/underflow.
            EOFError: If input stream closes during a READ operation.
            Exception: Re-raises any other unexpected exceptions during execution.
        """
        # 1. Check Program Counter bounds
        if not (0 <= self.program_counter <= self.MAX_MEMORY_ADDRESS):
            raise RuntimeError(f"Program Counter ({self.PC_FORMAT.format(self.program_counter)}) out of bounds ({self.MEM_RANGE_DISPLAY}). Execution halted.")

        # 2. Fetch instruction
        instruction_word = self.get_memory_value(self.program_counter)

        # 3. Validate instruction format (must be positive for opcodes)
        if instruction_word < 0:
            raise ValueError(f"Invalid instruction at address {self.PC_FORMAT.format(self.program_counter)}: Instruction word {self._format_word(instruction_word)} cannot be negative.")

        # 4. Decode opcode and operand (6-digit format: OO O AAA)
        opcode = instruction_word // 1000  # First 3 digits form the opcode
        operand = instruction_word % 1000   # Last 3 digits form the operand

        # 5. Validate operand address range
        if not (0 <= operand <= self.MAX_MEMORY_ADDRESS):
            raise ValueError(f"Operand {self.OPERAND_FORMAT.format(operand)} at address {self.PC_FORMAT.format(self.program_counter)} (Instruction: {self._format_word(instruction_word)}) references memory out of bounds ({self.MEM_RANGE_DISPLAY}).")

        # 6. Dispatch execution based on opcode
        execute_func = self._opcode_dispatch.get(opcode)

        next_pc = self.program_counter # Default, will be updated by handlers
        halt_execution = False

        if execute_func:
            try:
                next_pc, halt_execution = execute_func(operand)
                # Validate the next_pc returned by branch instructions
                if not (0 <= next_pc <= self.MAX_MEMORY_ADDRESS) and not halt_execution:
                     raise RuntimeError(f"Branch to invalid address {self.PC_FORMAT.format(next_pc)} from instruction at {self.PC_FORMAT.format(self.program_counter)}.")

            except (ValueError, ZeroDivisionError, OverflowError, RuntimeError, EOFError) as e:
                # Catch specific runtime errors from execution handlers or I/O
                print(f"\nRuntime Error at address {self.PC_FORMAT.format(self.program_counter)} (Instruction: {self._format_word(instruction_word)}): {e}", file=sys.stderr)
                halt_execution = True # Halt execution on error
                # Optionally re-raise if the calling context needs to handle it further
                # raise
            except Exception as e:
                 # Catch any other unexpected errors during execution
                 print(f"\nUnexpected Runtime Error at address {self.PC_FORMAT.format(self.program_counter)} (Instruction: {self._format_word(instruction_word)}): {e}", file=sys.stderr)
                 halt_execution = True
                 raise # Re-raise unexpected errors

        else:
            # Handle unknown opcode
            raise ValueError(f"Invalid opcode {opcode:03d} encountered at address {self.PC_FORMAT.format(self.program_counter)} (Instruction: {self._format_word(instruction_word)}).")

        # 7. Update state or halt
        if halt_execution:
            self.is_running = False
            return False # Signal halt/error
        else:
            self.program_counter = next_pc
            return True # Signal continue

    def run(self):
        """
        Executes the loaded 6-digit program until HALT or error.

        Raises:
            Exception: Propagates exceptions raised during step execution (e.g., RuntimeError, ValueError).
        """
        if self.is_running:
            print("Simulator is already running.", file=sys.stderr)
            return

        if not (0 <= self.program_counter <= self.MAX_MEMORY_ADDRESS):
             print(f"Cannot run: Initial Program Counter ({self.program_counter}) is out of bounds.", file=sys.stderr)
             return

        self.is_running = True
        try:
            while self.is_running:
                if not self.step(): # step() returns False on HALT or error
                    break
        except Exception as e:
            # Error message is already printed by step()
            self.is_running = False # Ensure state is updated
            # No need to re-raise usually, as step() handles logging.
            # If calling code needs the exception, uncomment the next line:
            # raise
        finally:
            # Ensure is_running is false if loop terminates unexpectedly
            self.is_running = False


    # --- Static Porting Method ---
    @staticmethod
    def port_4_to_6(lines_4_digit):
        """
        Converts a list of 4-digit BasicML lines to 6-digit lines. Static method.

        Args:
            lines_4_digit (list[str]): List of strings containing 4-digit code.

        Returns:
            list[str]: List of strings containing equivalent 6-digit code.

        Raises:
            ValueError: If conversion fails for a line due to format/range errors.
        """
        lines_6_digit = []
        map_4_to_6 = UVSim.OPCODE_4_TO_6_MAP # Use class attribute

        for i, line in enumerate(lines_4_digit):
            line = line.strip()
            # Preserve comments and empty lines
            if not line or line.startswith('#'):
                lines_6_digit.append(line)
                continue

            try:
                # --- Validate 4-digit format before porting ---
                # 1. Check length (sign + 4 digits)
                if len(line) != 5:
                     raise ValueError("Invalid 4-digit format length (must be 5 chars, e.g., +1099).")
                # 2. Check sign
                sign = line[0]
                if sign not in '+-':
                    raise ValueError("4-digit word must start with '+' or '-'.")

                # 3. Attempt conversion to integer (validates digits)
                val_4 = int(line)

                # 4. Determine if it's an instruction or data
                # Instruction: Starts with '+', first two digits are a known opcode
                raw_opcode_4 = int(line[1:3]) if sign == '+' else -1 # Get potential opcode
                is_instruction = (sign == '+' and raw_opcode_4 in map_4_to_6)

                if is_instruction:
                    # --- Convert Instruction ---
                    operand_4 = int(line[3:5]) # Get operand
                    # Validate 4-digit operand range (00-99)
                    if not (0 <= operand_4 <= 99):
                        raise ValueError(f"Invalid 4-digit operand '{line[3:5]}' (must be 00-99).")

                    # Map to 6-digit opcode
                    opcode_6 = map_4_to_6[raw_opcode_4]
                    # Operand value maps directly (0-99), will be padded later
                    operand_6 = operand_4
                    # Construct the 6-digit instruction word (OooAaa format)
                    # Note: Opcode needs to be scaled
                    new_word_val = opcode_6 * 1000 + operand_6
                    # Format as a 6-digit positive word
                    lines_6_digit.append(f"+{new_word_val:06d}")

                else:
                    # --- Convert Data Word ---
                    # Validate 4-digit data range (+/-9999)
                    if not (-9999 <= val_4 <= 9999):
                        raise ValueError(f"Data value {val_4} out of 4-digit range (-9999 to +9999).")
                    # Format as a 6-digit word, preserving sign and padding value
                    lines_6_digit.append(f"{sign}{abs(val_4):06d}")

            except Exception as e:
                 # Add line number context to any error during conversion
                 raise ValueError(f"Line {i+1}: Failed to convert 4-digit word '{line}'. Reason: {e}")

        return lines_6_digit

