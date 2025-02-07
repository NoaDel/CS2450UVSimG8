import pytest
from UVSim import UVSim

@pytest.fixture
def simulator():
    """Returns a fresh UVSim instance for each test."""
    return UVSim()

# I/O Operations Tests
def test_read_valid_input(simulator, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1234")
    simulator.read(50)
    assert simulator.memory[50] == 1234

def test_read_invalid_input(simulator, monkeypatch, capsys):
    monkeypatch.setattr('builtins.input', lambda _: "abc")
    simulator.read(50)
    captured = capsys.readouterr()
    assert "Error: Invalid input." in captured.out
    assert simulator.instruction_counter == 0 # Check if re-execute

def test_write(simulator, capsys):
    simulator.memory[30] = -987
    simulator.write(30)
    captured = capsys.readouterr()
    assert "Output: -987" in captured.out

def test_write_zero(simulator, capsys):
    simulator.memory[30] = 0
    simulator.write(30)
    captured = capsys.readouterr()
    assert "Output: 0" in captured.out

# Load/Store Operation Tests
def test_load(simulator):
    simulator.memory[25] = 7777
    simulator.load(25)
    assert simulator.accumulator == 7777

def test_load_negative(simulator):
    simulator.memory[10] = -1234
    simulator.load(10)
    assert simulator.accumulator == -1234

def test_store(simulator):
    simulator.accumulator = 4321
    simulator.store(60)
    assert simulator.memory[60] == 4321

def test_store_zero(simulator):
    simulator.accumulator = 0
    simulator.store(15)
    assert simulator.memory[15] == 0

# Arithmetic Operation Tests
def test_add(simulator):
    simulator.memory[40] = 2000
    simulator.accumulator = 3000
    assert simulator.add(40) == True
    assert simulator.accumulator == 5000

def test_add_overflow(simulator):
    simulator.memory[40] = 9999
    simulator.accumulator = 1
    assert simulator.add(40) == False

def test_subtract(simulator):
    simulator.memory[55] = 500
    simulator.accumulator = 1200
    assert simulator.subtract(55) == True
    assert simulator.accumulator == 700

def test_subtract_overflow(simulator):
    simulator.memory[55] = -9999
    simulator.accumulator = 1
    assert simulator.subtract(55) == False

def test_divide(simulator):
    simulator.memory[70] = 4
    simulator.accumulator = 20
    assert simulator.divide(70) == True
    assert simulator.accumulator == 5

def test_divide_by_zero(simulator):
    simulator.memory[70] = 0
    simulator.accumulator = 10
    assert simulator.divide(70) == False

def test_multiply(simulator):
    simulator.memory[80] = 3
    simulator.accumulator = 7
    assert simulator.multiply(80) == True
    assert simulator.accumulator == 21

def test_multiply_overflow(simulator):
    simulator.memory[80] = 5000
    simulator.accumulator = 3
    assert simulator.multiply(80) == False

# Control Operation Tests
def test_branch(simulator):
    simulator.branch(90)
    assert simulator.instruction_counter == 90

def test_branch_to_zero(simulator):
    simulator.branch(0)
    assert simulator.instruction_counter == 0

def test_branchneg_negative(simulator):
    simulator.accumulator = -5
    simulator.branchneg(33)
    assert simulator.instruction_counter == 33

def test_branchneg_positive(simulator):
    simulator.accumulator = 10
    simulator.branchneg(33)
    assert simulator.instruction_counter == 0 # Should not branch

def test_branchzero_zero(simulator):
    simulator.accumulator = 0
    simulator.branchzero(77)
    assert simulator.instruction_counter == 77

def test_branchzero_nonzero(simulator):
    simulator.accumulator = -2
    simulator.branchzero(77)
    assert simulator.instruction_counter == 0 # Should not branch

def test_halt(simulator):
    assert simulator.halt(0) == False

def test_halt_program(simulator, capsys):
    simulator.halt(0)
    captured = capsys.readouterr()
    assert "Program halted." in captured.out