import sys, os
import re
from Bio import SeqIO


fasta = sys.argv[1]
output = sys.argv[2]

total_number = 0
for record in SeqIO.parse(fasta, "fasta"):
    name = str(record.id)
    name = re.sub(r'\[|\]|\(|\)',"", name)
    total_number += 1
    with open(os.path.join(output, name+".txt"), "w") as f:
        f.write(f">{name}\n{str(record.seq)}\n")
print(f"total {total_number} files are splited")
