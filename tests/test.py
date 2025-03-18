
from language_processing_tool.process_pdfs import process_pdfs ,process_single_file

# Test: Call the function
# print(process_pdfs("/FE_Documents/ISIN/INE815R07022.pdf"))
print(process_single_file("/FE_Documents/ISIN/DE000DK0LA37.pdf"))

#in CMD
 

#Batch Processing (multiple PDFs):
#python sourcecode.py /FE_Documents/ISIN/ /home/harish/intern/language_clustering/filenames_csv.csv /home/harish 4

#Single PDF Processing:
#python sourcecode.py /FE_Documents/ISIN/ES1316617-ES1028292-ES1430422.pdf
