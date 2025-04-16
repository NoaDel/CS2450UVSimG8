import os

def port(input_file_path):
    """
    Reads a .txt file containing codes and adds two leading zeros to the numeric part of each code
    (behind the optional + or - sign). Saves the modified codes to a new file with "(port)" appended
    to the original filename.

    Args:
        input_file_path (str): The path to the input .txt file.
    """
    try:
        with open(input_file_path, 'r') as infile:
            lines = infile.readlines()

        base, ext = os.path.splitext(input_file_path)
        output_file_path = f"{base} (port){ext}"

        with open(output_file_path, 'w') as outfile:
            for line in lines:
                cleaned_line = line.strip()
                if cleaned_line:
                    sign = ""
                    code_part = cleaned_line
                    if cleaned_line.startswith('+') or cleaned_line.startswith('-'):
                        sign = cleaned_line[0]
                        code_part = cleaned_line[1:]

                    if code_part.isdigit():
                        padded_code = sign + "00" + code_part
                        outfile.write(padded_code + '\n')
                    else:
                        outfile.write(cleaned_line + '\n')
                else:
                    outfile.write('\n')
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")