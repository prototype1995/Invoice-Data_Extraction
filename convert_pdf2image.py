"""
A Python script to convert a multi-page PDF to a directory of images
Uses the pdf2image package
"""

from pdf2image import convert_from_path
import os


file_path = 'pgm_files/sample.pdf'
out_folder = 'output'

def pdftoimage(fileName, output_folder):
    images = convert_from_path(fileName)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    index = 1
    for i, image in enumerate(images):
#        fname = 'image'+str(i)+'.jpg'
        strFileName=str(index)+".jpg"
        outFilename = os.path.join(output_folder,  strFileName)
        image.save(outFilename)
        index += 1
    return 2
