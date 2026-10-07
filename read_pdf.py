from pypdf import PdfReader
import re
import xlsxwriter
import pdfplumber
# Load your PDF file
reader = PdfReader("./cpc-scheme-H.pdf")
row=0
row_names = ['file name', 'Patent classification codes','patent key words','patent classification description', 'patent text', ]

workbook=None
worksheet=None

def extract_patent_codes():
    cpc_classification = []
    with pdfplumber.open("./cpc-scheme-H.pdf") as pdf:
        for i, page in enumerate(pdf.pages):
            width = page.width
            height = page.height
            # Define bounding boxes for left and right columns (x0, y0, x1, y1)
            left_bbox = (0, 0, width / 6, height)
            right_bbox = (width / 6, 0, width, height)
            # Extract text from each column
            left_text = page.crop(left_bbox).extract_text()
            right_text = page.crop(right_bbox).extract_text()
            cpc_classification.append([left_text,right_text])
            #print(f"--- Page {i+1} ---")
            #print("LEFT COLUMN:\n", left_text)
            #print("\nRIGHT COLUMN:\n", right_text)
    return cpc_classification

def write_data_to_worksheet(file_name, cpc_code, patent_key_words, patent_text, patent_classification_description):
    global workbook
    global worksheet
    global row
    try:
        if (workbook==None):
            workbook = xlsxwriter.Workbook('patent_class_result.xlsx')
            worksheet = workbook.add_worksheet()
            worksheet.set_column(0, 4, 150)
            worksheet.write_row(row,0,row_names)     
            row=1   
        row_strings = [file_name, cpc_code, patent_key_words, patent_text, patent_classification_description]
        worksheet.write_row(row,0, row_strings)
        row=row+1
    except Exception as e:
        print(e)

def close_workbook():
    global workbook
    global worksheet
    if (workbook!=None):
        workbook.close()