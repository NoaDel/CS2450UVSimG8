import unittest
import io
import sys
from unittest.mock import patch, MagicMock

# Assuming the UVSim class is in uvsim_core_logic.py
try:
    from uvsim_core_logic import UVSim
except ImportError:
    print("FATAL ERROR: Could not import UVSim from uvsim_core_logic.py.", file=sys.stderr)
    # Define a dummy class to prevent NameErrors in tests if import fails,
    # but tests requiring UVSim will likely fail anyway.
    class UVSim: pass
    # Or simply raise the ImportError to halt testing immediately
    # raise ImportError("UVSim class not found. Ensure uvsim_core_logic.py is accessible.")


class TestUVSimCore(unittest.TestCase):
    """Unit tests for the UVSim simulator class (6-digit only)."""

    def setUp(self):
        """Create a new UVSim instance for each test."""
        # Ensure UVSim was actually imported before proceeding
        if 'UVSim' not in globals() or not hasattr(UVSim, 'READ'): # Check for class and a known attribute
             self.skipTest("UVSim class not properly imported or defined.")

        self.mock_input_values = []
        self.mock_output_values = []
        # Redirect stderr for capturing error messages from step()
        self.held_stderr = sys.stderr
        sys.stderr = io.StringIO()
        self.sim = UVSim(io_read_func=self.mock_read, io_write_func=self.mock_write)

    def tearDown(self):
        """Restore stderr."""
        # Ensure stderr is restored even if setUp skipped the test
        if hasattr(self, 'held_stderr'):
            sys.stderr = self.held_stderr

    def mock_read(self):
        """Mock function to simulate reading user input."""
        if not self.mock_input_values:
            raise EOFError("Mock input list empty.")
        value_str = self.mock_input_values.pop(0)
        try:
            value = int(value_str)
            # Use class constants for range check
            if not (UVSim.MIN_WORD_VALUE <= value <= UVSim.MAX_WORD_VALUE):
                 raise ValueError(f"Mock input {value} out of range ({UVSim.MIN_WORD_VALUE} to {UVSim.MAX_WORD_VALUE}).")
            return value
        except ValueError as e:
            # Improve error message for debugging
            raise ValueError(f"Invalid mock input format or value: '{value_str}'. Original error: {e}")
        except EOFError: # Should be caught by the initial check, but good practice
            raise EOFError("Attempted to read past end of mock input.")


    def mock_write(self, value):
        """Mock function to capture output from WRITE operations."""
        self.mock_output_values.append(value)

    # --- Test Initialization and Reset (Always 6-Digit) ---
    def test_initialization_defaults_6_digit(self):
        """Verify initial state is always 6-digit."""
        self.assertEqual(self.sim.WORD_LENGTH, 6)
        self.assertEqual(self.sim.MAX_MEMORY_ADDRESS, 249)
        self.assertEqual(self.sim.MAX_WORD_VALUE, 999999)
        self.assertEqual(self.sim.MIN_WORD_VALUE, -999999)
        self.assertEqual(self.sim.accumulator, 0)
        self.assertEqual(self.sim.program_counter, 0)
        self.assertFalse(self.sim.is_running)
        # Check memory initialization (key addresses and size)
        self.assertEqual(self.sim.memory.get(0, None), 0) # Check default value is 0
        self.assertEqual(self.sim.memory.get(UVSim.MAX_MEMORY_ADDRESS, None), 0)
        self.assertEqual(len(self.sim.memory), UVSim.MAX_MEMORY_ADDRESS + 1) # Should be 250 words

    def test_reset_clears_state_6_digit(self):
        """Verify reset restores initial 6-digit state."""
        # Modify state
        self.sim.accumulator = 123456
        self.sim.program_counter = 10
        self.sim.memory[5] = 987654
        self.sim.is_running = True
        # Reset
        self.sim.reset()
        # Verify reset state
        self.assertEqual(self.sim.accumulator, 0)
        self.assertEqual(self.sim.program_counter, 0)
        self.assertFalse(self.sim.is_running)
        self.assertEqual(self.sim.memory.get(5, 0), 0) # Ensure previously set memory is cleared
        self.assertEqual(len(self.sim.memory), UVSim.MAX_MEMORY_ADDRESS + 1)

    # --- Test Format Detection (Static Method - Used by GUI) ---
    def test_detect_format_6_digit(self):
        lines = ["+100001", "+200002", "-000005"]
        self.assertEqual(UVSim.detect_format(lines), 6)

    def test_detect_format_4_digit(self):
        lines = ["+1001", "+2002", "-0005"]
        self.assertEqual(UVSim.detect_format(lines), 4)

    def test_detect_format_mixed(self):
        lines = ["+100001", "+2002"]
        with self.assertRaisesRegex(ValueError, "Mixed format detected"):
            UVSim.detect_format(lines)

    def test_detect_format_invalid_length(self):
        lines = ["+12345"] # 5 digits after sign
        with self.assertRaisesRegex(ValueError, "Invalid word length"):
            UVSim.detect_format(lines)
        lines_long = ["+1234567"] # 7 digits after sign
        with self.assertRaisesRegex(ValueError, "Invalid word length"):
            UVSim.detect_format(lines_long)

    def test_detect_format_invalid_char(self):
        lines = ["+12345X"]
        with self.assertRaisesRegex(ValueError, "Invalid number format"):
            UVSim.detect_format(lines)

    def test_detect_format_no_sign(self):
        lines = ["100001"]
        with self.assertRaisesRegex(ValueError, "Must start with"):
            UVSim.detect_format(lines)

    def test_detect_format_empty_or_comments(self):
        lines = ["", "# comment", "   ", "# another comment"]
        # Should default to 6 if no actual code lines are found
        self.assertEqual(UVSim.detect_format(lines), 6)
        lines_with_code = ["# comment", "+100000", "   "]
        self.assertEqual(UVSim.detect_format(lines_with_code), 6)


    # --- Test Program Loading (Always 6-Digit) ---
    def test_load_program_6_digit_success(self):
        lines = ["+010005", # READ 005
                 "+043000", # HALT
                 "# comment",
                 "+000000", # Data/Padding
                 "-123456"] # Data
        self.assertTrue(self.sim.load_program_from_lines(lines))
        self.assertEqual(self.sim.WORD_LENGTH, 6) # Verify mode didn't change
        self.assertEqual(self.sim.MAX_MEMORY_ADDRESS, 249)
        # Check loaded values
        self.assertEqual(self.sim.memory[0], 10005)
        self.assertEqual(self.sim.memory[1], 43000)
        self.assertEqual(self.sim.memory[2], 0) # Should load 0 for the data word "+000000"
        self.assertEqual(self.sim.memory[3], -123456) # Should load negative data
        # Check state after load
        self.assertEqual(self.sim.program_counter, 0)
        self.assertFalse(self.sim.is_running)

    def test_load_program_exceeds_limit_6_digit(self):
        lines = [f"+000000"] * (UVSim.MAX_MEMORY_ADDRESS + 2) # 251 lines of code
        with self.assertRaisesRegex(ValueError, "exceeds memory limit"):
            self.sim.load_program_from_lines(lines)

    def test_load_program_invalid_value_range_6(self):
        """Test loading values outside the +/-999999 range (length check happens first)."""
        # These have incorrect length (8 chars), so length error is raised first.
        lines_pos_oor = ["+1000000"] # Value too large, length 8
        with self.assertRaisesRegex(ValueError, "Expected 7 characters"):
             self.sim.load_program_from_lines(lines_pos_oor)
        lines_neg_oor = ["-1000000"] # Value too small, length 8
        with self.assertRaisesRegex(ValueError, "Expected 7 characters"):
             self.sim.load_program_from_lines(lines_neg_oor)

        # Test boundary values (should load successfully)
        self.assertTrue(self.sim.load_program_from_lines(["+999999"]))
        self.assertEqual(self.sim.memory[0], 999999)
        self.assertTrue(self.sim.load_program_from_lines(["-999999"]))
        self.assertEqual(self.sim.memory[0], -999999)


    def test_load_program_invalid_format_6(self):
        """Test various format errors during loading."""
        lines_len_short = ["+12345"] # Too short (6 chars)
        with self.assertRaisesRegex(ValueError, "Expected 7 characters"):
            self.sim.load_program_from_lines(lines_len_short)
        lines_len_long = ["+1234567"] # Too long (8 chars)
        with self.assertRaisesRegex(ValueError, "Expected 7 characters"):
            self.sim.load_program_from_lines(lines_len_long)

        lines_no_sign = ["010005"] # Missing sign (6 chars)
        # Length check fails first
        with self.assertRaisesRegex(ValueError, "Expected 7 characters"):
            self.sim.load_program_from_lines(lines_no_sign)

        lines_bad_sign = ["*123456"] # Invalid sign (7 chars)
        # Sign check fails
        with self.assertRaisesRegex(ValueError, "Word must start with"):
            self.sim.load_program_from_lines(lines_bad_sign)

        lines_char = ["+12345X"] # Invalid character (7 chars)
        # int() conversion fails
        with self.assertRaisesRegex(ValueError, "Invalid 6-digit word format"):
             self.sim.load_program_from_lines(lines_char)


    # --- Test Instruction Execution (Always 6-Digit) ---

    def test_step_read_6(self):
        program = ["+010002", "+043000", "+000000"] # READ into 002
        self.mock_input_values = ["+123456"]
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # Execute READ
        self.assertEqual(self.sim.memory[2], 123456)
        self.assertEqual(self.sim.program_counter, 1)

    def test_step_read_invalid_input_range_6(self):
        program = ["+010002", "+043000", "+000000"]
        self.mock_input_values = ["+1000000"] # Value out of UVSim range
        self.assertTrue(self.sim.load_program_from_lines(program))
        # step() calls mock_read, which raises ValueError. step() catches it.
        self.assertFalse(self.sim.step()) # Step should return False on error
        self.assertFalse(self.sim.is_running) # is_running should be False
        self.assertEqual(self.sim.program_counter, 0) # PC should not advance
        # Check stderr for the error message logged by step()
        error_output = sys.stderr.getvalue()
        self.assertIn("Runtime Error at address 000", error_output)
        self.assertIn("Mock input 1000000 out of range", error_output)


    def test_step_read_eof_6(self):
        program = ["+010002", "+043000", "+000000"]
        self.mock_input_values = [] # No input provided
        self.assertTrue(self.sim.load_program_from_lines(program))
        # step() calls mock_read, which raises EOFError. step() catches it.
        self.assertFalse(self.sim.step()) # Step should return False on error
        self.assertFalse(self.sim.is_running) # is_running should be False
        self.assertEqual(self.sim.program_counter, 0) # PC shouldn't advance
        # Check stderr for the error message logged by step()
        error_output = sys.stderr.getvalue()
        self.assertIn("Runtime Error at address 000", error_output)
        self.assertIn("Mock input list empty", error_output)


    def test_step_write_6(self):
        program = ["+011002", "+043000", "+987654"] # WRITE from 002
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # Execute WRITE
        self.assertEqual(self.mock_output_values, [987654])
        self.assertEqual(self.sim.program_counter, 1)

    def test_step_load_6(self):
        program = ["+020002", "+043000", "+112233"] # LOAD from 002
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # Execute LOAD
        self.assertEqual(self.sim.accumulator, 112233)
        self.assertEqual(self.sim.program_counter, 1)

    def test_step_store_6(self):
        # Load 555555 first, then store it
        program = ["+020003", "+021004", "+043000", "+555555", "+000000"] # LOAD 003, STORE 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        # Step 1: LOAD
        self.assertTrue(self.sim.step())
        self.assertEqual(self.sim.accumulator, 555555)
        self.assertEqual(self.sim.program_counter, 1)
        # Step 2: STORE
        self.assertTrue(self.sim.step())
        self.assertEqual(self.sim.memory[4], 555555) # Check memory location 004
        self.assertEqual(self.sim.program_counter, 2)

    def test_step_add_6(self):
        # Load 5, then add 10
        program = ["+020003", "+030004", "+043000", "+000005", "+000010"] # LOAD 003, ADD 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # ADD
        self.assertEqual(self.sim.accumulator, 15)
        self.assertEqual(self.sim.program_counter, 2)

    def test_step_add_overflow_6(self):
        # Load MAX, then add 1
        program = ["+020003", "+030004", "+043000", f"+{UVSim.MAX_WORD_VALUE:06d}", "+000001"]
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        # ADD should cause overflow, step() catches it.
        self.assertFalse(self.sim.step()) # Step returns False on error
        # Check state after failed step
        self.assertFalse(self.sim.is_running)
        self.assertEqual(self.sim.program_counter, 1) # PC shouldn't advance
        # Check stderr for the error message logged by step()
        error_output = sys.stderr.getvalue()
        self.assertIn("Runtime Error at address 001", error_output)
        self.assertIn("Arithmetic overflow/underflow", error_output)


    def test_step_subtract_6(self):
        # Load 10, then subtract 3
        program = ["+020003", "+031004", "+043000", "+000010", "+000003"] # LOAD 003, SUB 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # SUBTRACT
        self.assertEqual(self.sim.accumulator, 7)
        self.assertEqual(self.sim.program_counter, 2)

    def test_step_subtract_underflow_6(self):
        # Load MIN, then subtract 1
        program = ["+020003", "+031004", "+043000", f"{UVSim.MIN_WORD_VALUE:+07d}", "+000001"] # Use sign formatting
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        # SUBTRACT should cause underflow, step() catches it.
        self.assertFalse(self.sim.step()) # Step returns False on error
        # Check state after failed step
        self.assertFalse(self.sim.is_running)
        self.assertEqual(self.sim.program_counter, 1) # PC shouldn't advance
        # Check stderr for the error message logged by step()
        error_output = sys.stderr.getvalue()
        self.assertIn("Runtime Error at address 001", error_output)
        self.assertIn("Arithmetic overflow/underflow", error_output)


    def test_step_divide_6(self):
        # Load 10, then divide by 3
        program = ["+020003", "+032004", "+043000", "+000010", "+000003"] # LOAD 003, DIV 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # DIVIDE
        self.assertEqual(self.sim.accumulator, 3) # Integer division
        self.assertEqual(self.sim.program_counter, 2)
        # Test negative division
        self.sim.reset()
        # Must reset stderr as well if checking output multiple times in one test
        sys.stderr = io.StringIO()
        program_neg = ["+020003", "+032004", "+043000", "-000010", "+000003"] # LOAD -10, DIV 3
        self.assertTrue(self.sim.load_program_from_lines(program_neg))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # DIVIDE
        self.assertEqual(self.sim.accumulator, -3) # Truncates towards zero
        self.assertEqual(self.sim.program_counter, 2)


    def test_step_divide_by_zero_6(self):
        # Load 10, then divide by 0
        program = ["+020003", "+032004", "+043000", "+000010", "+000000"] # LOAD 003, DIV 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        # DIVIDE should raise error, step() catches it.
        self.assertFalse(self.sim.step()) # Step returns False on error
        # Check state after failed step
        self.assertFalse(self.sim.is_running)
        self.assertEqual(self.sim.program_counter, 1) # PC shouldn't advance
        # Check stderr for the error message logged by step()
        error_output = sys.stderr.getvalue()
        self.assertIn("Runtime Error at address 001", error_output)
        self.assertIn("Division by zero", error_output)


    def test_step_multiply_6(self):
        # Load 10, then multiply by 5
        program = ["+020003", "+033004", "+043000", "+000010", "+000005"] # LOAD 003, MUL 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # MULTIPLY
        self.assertEqual(self.sim.accumulator, 50)
        self.assertEqual(self.sim.program_counter, 2)

    def test_step_multiply_overflow_6(self):
        # Load value, then multiply by 2 causing overflow
        start_val = UVSim.MAX_WORD_VALUE // 2 + 1
        program = ["+020003", "+033004", "+043000", f"+{start_val:06d}", "+000002"]
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        # MULTIPLY should cause overflow, step() catches it.
        self.assertFalse(self.sim.step()) # Step returns False on error
        # Check state after failed step
        self.assertFalse(self.sim.is_running)
        self.assertEqual(self.sim.program_counter, 1) # PC shouldn't advance
        # Check stderr for the error message logged by step()
        error_output = sys.stderr.getvalue()
        self.assertIn("Runtime Error at address 001", error_output)
        self.assertIn("Arithmetic overflow/underflow", error_output)


    def test_step_branch_6(self):
        program = ["+040003", "+000001", "+043000", "+000002"] # BRANCH 003
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # Execute BRANCH
        self.assertEqual(self.sim.program_counter, 3) # PC jumps to operand

    def test_step_branchneg_taken_6(self):
        # Load -10, then branch if neg
        program = ["+020003", "+041004", "+043000", "-000010", "+000000"] # LOAD 003, BRANCHNEG 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # BRANCHNEG
        self.assertEqual(self.sim.program_counter, 4) # Should jump

    def test_step_branchneg_not_taken_6(self):
        # Load +10, then branch if neg
        program = ["+020003", "+041004", "+043000", "+000010", "+000000"] # LOAD 003, BRANCHNEG 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # BRANCHNEG
        self.assertEqual(self.sim.program_counter, 2) # Should NOT jump, PC increments

    def test_step_branchzero_taken_6(self):
        # Load 0, then branch if zero
        program = ["+020003", "+042004", "+043000", "+000000", "+000000"] # LOAD 003, BRANCHZERO 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # BRANCHZERO
        self.assertEqual(self.sim.program_counter, 4) # Should jump

    def test_step_branchzero_not_taken_6(self):
        # Load 1, then branch if zero
        program = ["+020003", "+042004", "+043000", "+000001", "+000000"] # LOAD 003, BRANCHZERO 004
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertTrue(self.sim.step()) # LOAD
        self.assertTrue(self.sim.step()) # BRANCHZERO
        self.assertEqual(self.sim.program_counter, 2) # Should NOT jump, PC increments

    def test_step_halt_6(self):
        program = ["+043000"]
        self.assertTrue(self.sim.load_program_from_lines(program))
        self.assertFalse(self.sim.step()) # HALT returns False
        self.assertFalse(self.sim.is_running)
        self.assertEqual(self.sim.program_counter, 0) # PC doesn't advance on HALT step itself

    # --- Test Runtime Errors (Always 6-Digit) ---
    def test_step_invalid_opcode_6(self):
        program = ["+055000", "+043000"] # 55 is not a valid opcode
        self.assertTrue(self.sim.load_program_from_lines(program))
        # step() raises ValueError for invalid opcode
        with self.assertRaisesRegex(ValueError, "Invalid opcode 055"):
            self.sim.step()
        # Check state after failed step
        self.assertFalse(self.sim.is_running) # Should be set by step's error handling
        self.assertEqual(self.sim.program_counter, 0) # PC shouldn't advance


    def test_step_memory_out_of_bounds_operand_6(self):
        # LOAD from address 300 (out of bounds 0-249)
        program = ["+020300"]
        self.assertTrue(self.sim.load_program_from_lines(program))
        # step() raises ValueError for invalid operand
        with self.assertRaisesRegex(ValueError, "Operand 300 .* references memory out of bounds"):
            self.sim.step()
        # Check state after failed step
        self.assertFalse(self.sim.is_running) # Should be set by step's error handling
        self.assertEqual(self.sim.program_counter, 0) # PC shouldn't advance


    def test_step_pc_out_of_bounds_6(self):
        """Test error when PC itself is out of bounds."""
        # Set PC manually to an invalid address
        self.sim.program_counter = 250
        # step() should raise RuntimeError *before* fetching instruction
        # CORRECTED: Escape parentheses in regex
        with self.assertRaisesRegex(RuntimeError, "Program Counter \\(250\\) out of bounds"):
            self.sim.step()
        # Check state after failed step
        self.assertFalse(self.sim.is_running) # Should remain False or be set False
        self.assertEqual(self.sim.program_counter, 250) # PC remains where it was


    def test_step_invalid_instruction_negative_6(self):
        """Test error when instruction word itself is negative."""
        self.sim.reset()
        self.sim.memory[0] = -10000 # Put invalid instruction at PC=0
        # step() raises ValueError for negative instruction
        with self.assertRaisesRegex(ValueError, "Instruction word .* cannot be negative"):
            self.sim.step()
        # Check state after failed step
        self.assertFalse(self.sim.is_running) # Should be set by step's error handling
        self.assertEqual(self.sim.program_counter, 0) # PC shouldn't advance


    # --- Test Run Function (Simple Integration - Always 6-Digit) ---
    def test_run_simple_program_6(self):
        """Test a basic program that reads, loads, writes, and halts."""
        program = [ "+010004", # READ into 004
                    "+020004", # LOAD from 004
                    "+011004", # WRITE from 004
                    "+043000", # HALT
                    "+000000"  # Data storage at 004
                  ]
        self.mock_input_values = ["+777777"]
        self.assertTrue(self.sim.load_program_from_lines(program))
        # Run the program
        self.sim.run()
        # Verify final state and output
        self.assertEqual(self.sim.accumulator, 777777)
        self.assertEqual(self.mock_output_values, [777777])
        self.assertFalse(self.sim.is_running) # Should halt
        # PC should be at the location *after* the HALT instruction was executed from
        # HALT was at index 3, so PC should be 3 after step() returns False.
        self.assertEqual(self.sim.program_counter, 3)

    def test_run_program_step_runtime_error_6(self):
        """Test run stops correctly when a step causes a runtime error."""
        # Program attempts division by zero
        program = ["+020002", # LOAD from 002 (value 10)
                   "+032003", # DIVIDE by 003 (value 0)
                   "+000010", # Data 10
                   "+000000"  # Data 0
                  ]
        self.assertTrue(self.sim.load_program_from_lines(program))
        # Run should execute step 1 (LOAD), then fail on step 2 (DIVIDE)
        # run() catches the error, logs it, and stops.
        self.sim.run()
        # Verify state after run stopped due to error
        self.assertFalse(self.sim.is_running)
        self.assertEqual(self.sim.program_counter, 1) # PC stopped at the failing instruction
        self.assertEqual(self.sim.accumulator, 10) # Accumulator holds value before failed DIVIDE
        # Check stderr for the error message logged by step() via run()
        error_output = sys.stderr.getvalue()
        self.assertIn("Runtime Error at address 001", error_output)
        self.assertIn("Division by zero", error_output)


# --- Tests for Porting Logic (Now uses static UVSim.port_4_to_6) ---
class TestPortingLogic(unittest.TestCase):
    """Unit tests for the static UVSim.port_4_to_6 method."""

    # No setUp/tearDown needed for static method testing

    def test_port_instruction_simple(self):
        lines_4 = ["+1005", "+2006", "+4300"]
        expected_6 = ["+010005", "+020006", "+043000"]
        self.assertEqual(UVSim.port_4_to_6(lines_4), expected_6)

    def test_port_data_words(self):
        lines_4 = ["+0012", "-3456", "+0000", "-0001"]
        expected_6 = ["+000012", "-003456", "+000000", "-000001"]
        self.assertEqual(UVSim.port_4_to_6(lines_4), expected_6)

    def test_port_with_comments_and_blanks(self):
        lines_4 = ["# Start", "+2001", "", "# Data", "+1234", "  ", "-0005"]
        # CORRECTED: Expected output should have '' for the stripped whitespace line
        expected_6 = ["# Start", "+020001", "", "# Data", "+001234", "", "-000005"]
        self.assertEqual(UVSim.port_4_to_6(lines_4), expected_6)

    def test_port_all_opcodes(self):
        lines_4 = ["+1010", "+1111", "+2020", "+2121", "+3030", "+3131", "+3232", "+3333", "+4040", "+4141", "+4242", "+4343"]
        expected_6 = ["+010010", "+011011", "+020020", "+021021", "+030030", "+031031", "+032032", "+033033", "+040040", "+041041", "+042042", "+043043"]
        self.assertEqual(UVSim.port_4_to_6(lines_4), expected_6)

    def test_port_invalid_4_digit_length(self):
        lines_4_long = ["+12345"] # 5 digits after sign (len 6)
        # CORRECTED: Expect length error
        with self.assertRaisesRegex(ValueError, "Invalid 4-digit format length"):
            UVSim.port_4_to_6(lines_4_long)
        lines_4_short = ["+123"] # 3 digits after sign (len 4)
        # CORRECTED: Expect length error
        with self.assertRaisesRegex(ValueError, "Invalid 4-digit format length"):
            UVSim.port_4_to_6(lines_4_short)

    def test_port_invalid_4_digit_operand_range(self):
        """Test porting fails if 4-digit operand is out of range (00-99)."""
        lines_4 = ["+1099"] # Operand 99 is valid
        self.assertEqual(UVSim.port_4_to_6(lines_4), ["+010099"])

        lines_4_bad_len = ["+10100"] # Operand 100 is invalid, but length is also wrong (len 6)
        # CORRECTED: Expect length error first
        with self.assertRaisesRegex(ValueError, "Invalid 4-digit format length"):
            UVSim.port_4_to_6(lines_4_bad_len)

        # Test case with correct length (5) but invalid operand value (not possible with 2 digits 00-99)
        # The check `if not (0 <= operand_4 <= 99):` covers this implicitly.

    def test_port_invalid_4_digit_data_range(self):
        """Test porting fails on data outside 4-digit range (+/-9999) - length checked first."""
        # These have incorrect length (6 chars)
        lines_4_pos_oor = ["+10000"]
        # CORRECTED: Expect length error first
        with self.assertRaisesRegex(ValueError, "Invalid 4-digit format length"):
             UVSim.port_4_to_6(lines_4_pos_oor)
        lines_4_neg_oor = ["-10000"]
        # CORRECTED: Expect length error first
        with self.assertRaisesRegex(ValueError, "Invalid 4-digit format length"):
             UVSim.port_4_to_6(lines_4_neg_oor)

        # Check boundary values (These have correct length 5)
        self.assertEqual(UVSim.port_4_to_6(["+9999"]), ["+009999"])
        self.assertEqual(UVSim.port_4_to_6(["-9999"]), ["-009999"])

    def test_port_invalid_4_digit_format(self):
        """Test various format errors during porting."""
        lines_no_sign = ["1005"] # Length 4, incorrect
        # CORRECTED: Expect length error first
        with self.assertRaisesRegex(ValueError, "Invalid 4-digit format length"):
            UVSim.port_4_to_6(lines_no_sign)

        # Test invalid sign with correct length
        lines_bad_sign_correct_len = ["*1234"] # Length 5
        with self.assertRaisesRegex(ValueError, "4-digit word must start with"):
             UVSim.port_4_to_6(lines_bad_sign_correct_len)

        # Test invalid char with correct length
        lines_bad_char = ["+10AB"] # Length 5
        with self.assertRaisesRegex(ValueError, "invalid literal for int"): # Error from int() conversion
            UVSim.port_4_to_6(lines_bad_char)


if __name__ == "__main__":
    # Discover and run tests
    unittest.main(verbosity=2)
