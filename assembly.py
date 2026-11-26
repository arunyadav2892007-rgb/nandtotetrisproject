
import sys
import re

def assemble(filepath, k):

    comp_dict = {
        "0":"0101010", "1":"0111111", "-1":"0111010",
        "D":"0001100", "A":"0110000", "M":"1110000",
        "!D":"0001101", "!A":"0110001", "!M":"1110001",
        "-D":"0001111", "-A":"0110011", "-M":"1110011",
        "D+1":"0011111", "A+1":"0110111", "M+1":"1110111",
        "D-1":"0001110", "A-1":"0110010", "M-1":"1110010",
        "D+A":"0000010", "D+M":"1000010",
        "D-A":"0010011", "D-M":"1010011",
        "A-D":"0000111", "M-D":"1000111",
        "D&A":"0000000", "D&M":"1000000",
        "D|A":"0010101", "D|M":"1010101"
    }

    dest_dict = {
        "null":"000", "M":"001", "D":"010", "MD":"011",
        "A":"100", "AM":"101", "AD":"110", "AMD":"111"
    }

    jump_dict = {
        "null":"000", "JGT":"001", "JEQ":"010", "JGE":"011",
        "JLT":"100", "JNE":"101", "JLE":"110", "JMP":"111"
    }

    sym_table = {
        "SP":0, "LCL":1, "ARG":2, "THIS":3, "THAT":4,
        "SCREEN":16384, "KBD":24576
    }

    for i in range(16):
        sym_table["R" + str(i)] = i

    # Read file and preserve original line numbers
    with open(filepath, "r") as f:
        lines = []

        for line_number, line in enumerate(f, 1):
            line = line.split("//")[0].strip()

            if line:
                lines.append((line, line_number))

    # FIRST PASS: Find labels
    pc = 0
    instructions = []

    for line, line_number in lines:

        if line.startswith("(") and line.endswith(")"):

            label = line[1:-1]

            if not label or not re.match(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$", label):
                print(f"Line {line_number}: invalid label")
                return

            if label in sym_table:
                print(f"Line {line_number}: duplicate or reserved label")
                return

            sym_table[label] = pc

        else:
            instructions.append((line, line_number))
            pc += 1

    # SECOND PASS: Convert instructions
    var_addr = 16
    out_lines = []

    for line, line_number in instructions:

        try:

            if line.startswith("@"):

                val = line[1:]

                if not val:
                    raise ValueError("missing A-instruction value")

                if val.isdigit():
                    addr = int(val)

                else:
                    if not re.match(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$", val):
                        raise ValueError("invalid symbol")

                    if val not in sym_table:
                        sym_table[val] = var_addr
                        var_addr += 1

                    addr = sym_table[val]

                if addr < 0 or addr > 32767:
                    raise ValueError("address out of range")

                out_lines.append(f"0{addr:015b}")

            else:

                if line.count("=") > 1 or line.count(";") > 1:
                    raise ValueError("invalid instruction format")

                dest = line.split("=")[0].strip() if "=" in line else "null"

                rest = line.split("=", 1)[1].strip() if "=" in line else line

                comp = rest.split(";")[0].strip() if ";" in rest else rest.strip()

                jump = rest.split(";")[1].strip() if ";" in rest else "null"

                if dest not in dest_dict:
                    raise ValueError("invalid destination")

                if comp not in comp_dict:
                    raise ValueError("invalid computation")

                if jump not in jump_dict:
                    raise ValueError("invalid jump")

                binary = "111" + comp_dict[comp] + dest_dict[dest] + jump_dict[jump]

                out_lines.append(binary)

        except ValueError as e:

            if k % 3 == 1:
                print(f"Line {line_number}: invalid instruction ({e})")
                return
            else:
                raise

    # Save machine code
    output_file = filepath.rsplit(".", 1)[0] + ".hack"

    with open(output_file, "w") as f:
        f.write("\n".join(out_lines) + "\n")

    print("Assembly successful!")
    print("Output saved to:", output_file)


if len(sys.argv) > 2:
    assemble(sys.argv[1], int(sys.argv[2]))
else:
    print("Usage: python assembly.py filename.asm K")
