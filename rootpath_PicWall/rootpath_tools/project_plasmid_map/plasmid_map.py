import os
import sys

from Bio import SeqIO


def deal_selected_list(id_file):
    f = open(id_file, "r")
    selected_list = [i.rstrip("\n") for i in f]
    f.close()
    return selected_list


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    AAV6_Kan_5End = os.path.join(base_dir, "AAV6_Kan_5End_Region.fa") 
    AAV6_Kan_3End = os.path.join(base_dir, "AAV6_Kan_3End_Region.fa")

    clonotype_file = sys.argv[1]
    id_file = sys.argv[2]
    output = sys.argv[3]  # output must be the last parmarater.
    # print(id_file)

    End5 = [str(record.seq) for record in SeqIO.parse(AAV6_Kan_5End, "fasta")]
    End3 = [str(record.seq) for record in SeqIO.parse(AAV6_Kan_3End, "fasta")]

    selected_list = deal_selected_list(id_file)
    # print(selected_list)

    for record in SeqIO.parse(clonotype_file, "fasta"):
        record_id = str(record.id)
        if record_id in selected_list:
            record_seq = End5[0]+str(record.seq)+End3[0]
            with open(output+"/"+record_id+".fa", "w") as f:
                f.write(">"+record_id+"\n"+record_seq+"\n")


if __name__ == '__main__':
    main()
