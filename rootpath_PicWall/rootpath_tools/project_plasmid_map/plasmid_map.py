import sys
from Bio import SeqIO

AAV6_Kan_5End = sys.argv[1] # "AAV6_Kan_5End_Region.fa"
AAV6_Kan_3End = sys.argv[2] # "AAV6_Kan_3End_Region.fa"
clonotype_file = sys.argv[3]
output = sys.argv[4]

End5 = [str(record.seq) for record in SeqIO.parse(AAV6_Kan_5End, "fasta")]
End3 = [str(record.seq) for record in SeqIO.parse(AAV6_Kan_3End, "fasta")]


for record in SeqIO.parse(clonotype_file, "fasta"):
    record_id = str(record.id)
    record_seq = End5[0]+str(record.seq)+End3[0]
    with open(output+"/"+record_id+".fa", "w") as f:
        f.write(">"+record_id+"\n"+record_seq+"\n")
