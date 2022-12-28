import sys

from Bio import SeqIO

fasta = sys.argv[1]
output = sys.argv[2]
a = 0
for record in SeqIO.parse(fasta,"fasta"):
    name = record.id
    a +=1
    with open(output+'/'+name+".txt", "w") as f:
        f.write(">{}\n{}\n".format(name,record.seq))
# print("total {} files are splited".format(a))
