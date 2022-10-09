from ast import alias
from cmath import exp
import sys
import pandas as pd
import openpyxl

def usage():
    print("Usage: re_pooling.py <input_file> <input2_file> <output_file>")
    sys.exit(1)

def write2excel(workbook, data_content, sheet_name, output):
    worksheet = workbook.create_sheet(title=sheet_name)
    title_content = ["Gene_ID",'Destination Plate Name','Destination well']
    worksheet.append(title_content)
    for each in data_content:
        worksheet.append(each)
    workbook.save(output + '/workbook.xlsx')

def deal_gene_list_file(gene_list_file):
    a_list = []
    df = pd.read_excel(gene_list_file, dtype=str, index_col=0) # index column is first column.
    a_list = df.index.to_list()
    return a_list

def subset_table(gene_id_list, table_array_file, output_file):
    workbook = openpyxl.Workbook()
    workbook.remove(workbook['Sheet']) # remove the empty worksheet.
    dfs = pd.read_excel(table_array_file, dtype=str, sheet_name=None)

    for each_sheet in dfs:
        df = dfs[each_sheet].drop_duplicates(subset=['Gene_ID'], keep='first')
        df.loc[:,'Gene_ID'] = df.loc[:,'Gene_ID'].str.split(".",expand=True)[0]
        df.set_index("Gene_ID", inplace=True)

        data_content = []
        for value in gene_id_list:
            if value in df.index:
                a=[value,]
                a.extend(df.loc[value, ['Destination Plate Name','Destination well']].values.tolist())
                data_content.append(a)
            else:
                data_content.append([value,"NA","NA"])
        write2excel(workbook=workbook, data_content=data_content, sheet_name=each_sheet, output=output_file)

def main():
    if len(sys.argv) != 4:
        usage()
    table_array_file = sys.argv[1]
    gene_list_file = sys.argv[2]
    output_file = sys.argv[3]

    gene_id_list = deal_gene_list_file(gene_list_file)
    subset_table(gene_id_list, table_array_file, output_file)
    

if __name__ == '__main__':
    main()
