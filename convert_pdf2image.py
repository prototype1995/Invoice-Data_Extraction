import pdf2image
from PIL import Image
import time
import os

#DECLARE CONSTANTS
#PDF_PATH = "C:/OCR/COI/OP00112177_IncomeProof_18012019_24623.pdf126421126_1.PDF"
DPI = 300
#OUTPUT_FOLDER = None
FIRST_PAGE = None
LAST_PAGE = None
FORMAT = 'jpg'
THREAD_COUNT = 1
USERPWD = None
USE_CROPBOX = False
STRICT = False


def pdftoimage(pdf_path,output_folder,filename):
    #This method reads a pdf and converts it into a sequence of images
    # very importent need to install poppler-0.68.0_x86 and setting C:\Program Files\poppler-0.68.0_x86\poppler-0.68.0\bin envirment veriabel
    #start_time = time.time()
    pil_images = pdf2image.convert_from_path(pdf_path, dpi=DPI)
    #pil_images = pdf2image.convert_from_path(pdf_path, dpi=DPI, output_folder=output_folder, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    #print ("output_folder Created")
    index = 1
    for image in pil_images:
        strFileName=str(index)+".jpg"
        #print(strFileName)
        outFilename = os.path.join(output_folder,  strFileName)
        #print(outFilename)
        image.save(outFilename)
        index += 1

    #print ("Time taken : " + str(time.time() - start_time))
    return 2
