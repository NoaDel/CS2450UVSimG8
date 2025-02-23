import tkinter as tk

class OutputHandler:
    output_box = None
    input_box = None
    """
    I recommend adding a terminal_box when making the box for integer arguments
    """
    value = 0 #Used for the hard-coded read function, edit if needed

    @classmethod
    def set_boxes(cls, output_box, input_box):
        """Sets the text output box and input box."""
        cls.output_box = output_box
        cls.input_box = input_box

    @classmethod
    def write_to_output(cls, text: str):
        """Writes text to the output window."""
        if cls.output_box:
            cls.output_box.config(state='normal')
            cls.output_box.insert('end', text + "\n")
            cls.output_box.config(state='disabled')
            cls.output_box.yview('end')
    
    @classmethod
    def get_int_input(cls):
        cls.write_to_output("Enter an integer:")
        cls.input_box.config(state='normal')  # Ensure input box remains active
        cls.input_box.focus()
        cls.input_box.bind("<Return>", cls.process_value())  # Bind Enter key
        # print(cls.value)
        return cls.value
    
    @classmethod
    def process_value(cls):
        if cls.input_box != None: #Delete this if condition if needed
            cls.value = 10 #Edit this line
        # print(cls.value)
