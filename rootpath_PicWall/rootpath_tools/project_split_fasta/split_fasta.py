import sys
import os
import re
from Bio import SeqIO

def parse_fasta_or_tab(file_path):
    records = []
    with open(file_path, "r") as file:
        if ">" in file.read(100):  # Check the first 100 characters for the ">" symbol
            # Assume it's a FASTA file
            records = list(SeqIO.parse(file_path, "fasta"))
        else:
            # Assume it's a text/tab-separated file
            file.seek(0)  # Reset file pointer
            for line in file:
                parts = line.strip().split('\t')  # Assuming tab-separated, modify for other delimiters
                if len(parts) >= 2:
                    name = re.sub(r'\[|\]|\(|\)', "", parts[0])
                    seq = parts[1]
                    records.append((name, seq))
    return records

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_directory")
        sys.exit(1)

    input_file = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    records = parse_fasta_or_tab(input_file)

    total_number = 0
    for record in records:
        name, seq = record
        total_number += 1
        with open(os.path.join(output_directory, f"{name}.txt"), "w") as f:
            f.write(f">{name}\n{seq}\n")

    print(f"Total {total_number} files are split")

if __name__ == "__main__":
    main()
