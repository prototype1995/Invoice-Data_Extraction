from google.cloud import vision
from google.cloud.vision import types

import os
import io
import re

from PIL import Image, ImageDraw
from enum import Enum


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="../recheckpython.json"

#image_file = 'Add your image file with path'

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


def data_retrieve(img):
    data = ''
    client = vision.ImageAnnotatorClient()
    with io.open(img, 'rb') as image_file:
            content = image_file.read()
    image = types.Image(content=content)
    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    annotations = response.text_annotations
    for text in annotations:
        data = text.description
        break
    return response, document, data

#response, document, text= data_retrieve(image_file)
#print(text) # Debugging

bounds = []

# Pattern Matching
def reg_expn(txt):
    '''
    Method to find matching regular expressions
    Returns : GSTIN, Mob num, Email
    '''
    # GSTIN
    gst_pattern = r'[0-3][0-9][A-Z][A-Z][A-Z][ABCFGHLJPT][A-Za-z][0-9][0-9][0-9][1-9][A-Z][12][Z2].'
    gst_values = re.findall(gst_pattern, txt)

    # Mobile Number
    mobNum_pattern = r'[(+91)]*[6-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
    mobNum_values = re.findall(mobNum_pattern, txt)

    # Email
    mail_pattern = r'([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})'
    mail_values = re.findall(mail_pattern, txt)

    return gst_values, mobNum_values, mail_values

#GST_values, MOB_nums, Mails = reg_expn(text)
#GST_values.append('GSTIN')

def draw_boxes(img, bounds, color,width=5):
    image = Image.open(img)
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        draw.line([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y,
            bound.vertices[0].x, bound.vertices[0].y],fill=color, width=width)
    return image

def get_document_bounds(response, feature, document):
    for i,page in enumerate(document.pages):
        for block in page.blocks:
            if feature==FeatureType.BLOCK:
                bounds.append(block.bounding_box)
            for paragraph in block.paragraphs:
                if feature==FeatureType.PARA:
                    bounds.append(paragraph.bounding_box)
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)
                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)
    return bounds

#bounds=get_document_bounds(response, FeatureType.BLOCK, document) # detection by block
#print(bounds) # Debugging

#img_withBoxes = draw_boxes(image_file, bounds, 'yellow')
#img_withBoxes.show() # Debugging


# Location of a particular word
def assemble_word(word):
    assembled_word=""
    for symbol in word.symbols:
        assembled_word+=symbol.text
    return assembled_word

def find_block_loc_from_word(document,word_to_find):
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    assembled_word=assemble_word(word)
                    if(assembled_word==word_to_find):
                        return block.bounding_box


# Find word from location
def text_within(document,x1,y1,x2,y2):
    text=""
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        min_x=min(symbol.bounding_box.vertices[0].x,symbol.bounding_box.vertices[1].x,symbol.bounding_box.vertices[2].x,symbol.bounding_box.vertices[3].x)
                        max_x=max(symbol.bounding_box.vertices[0].x,symbol.bounding_box.vertices[1].x,symbol.bounding_box.vertices[2].x,symbol.bounding_box.vertices[3].x)
                        min_y=min(symbol.bounding_box.vertices[0].y,symbol.bounding_box.vertices[1].y,symbol.bounding_box.vertices[2].y,symbol.bounding_box.vertices[3].y)
                        max_y=max(symbol.bounding_box.vertices[0].y,symbol.bounding_box.vertices[1].y,symbol.bounding_box.vertices[2].y,symbol.bounding_box.vertices[3].y)
                        if(min_x >= x1 and max_x <= x2 and min_y >= y1 and max_y <= y2):
                            text+=symbol.text
                            if(symbol.property.detected_break.type==1 or symbol.property.detected_break.type==3):
                                text+=' '
                            if(symbol.property.detected_break.type==2):
                                text+='\t'
                            if(symbol.property.detected_break.type==5):
                                text+='\n'
    return text

'''
try:
    data_coll = []
    final_data = []
    avoid_data = ['Adani', 'ADANI', 'Billing', 'Shipping', 'Bill', 'Ship']
    city_code_dict = {
                        '01' : 'Jammu & Kashmir',
                        '02' : 'Himachal Pradesh',
                        '03' : 'Punjab',
                        '04' : 'Chandigarh',
                        '05' : 'Uttarakhand',
                        '06' : 'Haryana',
                        '07' : 'Delhi',
                        '08' : 'Rajasthan',
                        '09' : 'Uttar Pradesh',
                        '10' : 'Bihar',
                        '11' : 'Sikkim',
                        '12' : 'Arunachal Pradesh',
                        '13' : 'Nagaland',
                        '14' : 'Manipur',
                        '15' : 'Mizoram',
                        '16' : 'Tripura',
                        '17' : 'Meghalaya',
                        '18' : 'Assam',
                        '19' : 'West Bengal',
                        '20' : 'Jharkhand',
                        '21' : 'Orissa',
                        '22' : 'Chhattisgarh',
                        '23' : 'Madhya Pradesh',
                        '24' : 'Gujarat',
                        '25' : 'Daman & Diu',
                        '26' : 'Dadra & Nagar Haveli',
                        '27' : 'Maharashtra',
                        '28' : 'Andhra Pradesh (Old)',
                        '29' : 'Karnataka',
                        '30' : 'Goa',
                        '31' : 'Lakshadweep',
                        '32' : 'Kerala',
                        '33' : 'Tamil Nadu',
                        '34' : 'Puducherry',
                        '35' : 'Andaman & Nicobar Islands',
                        '36' : 'Telengana',
                        '37' : 'Andhra Pradesh (New)'
    }

    for gst_value in GST_values:
#        print(gst_value) # Debugging
        state_code = gst_value[:2]
#        print(city_code_dict[state_code]) # Debugging
        location=find_block_loc_from_word(document,gst_value)
        #print(location) # Debugging
        # finding block wth containing word
        data = text_within(document, location.vertices[0].x, location.vertices[0].y, location.vertices[2].x,location.vertices[2].y)
        #print('\n'+data) # Debugging
        data_coll.append(data)
    data_coll = set(data_coll) # Done to avoid repetition
    for i in data_coll:
        for j in avoid_data:
            if i.find(j)!=-1:
                final_data.append(i)
    final_data = set(final_data) # avoid copies
    # removing invalid data from data_coll
    for data in final_data:
        data_coll.remove(data)
    for valid_data in data_coll:
        print(valid_data)

except:
    print('ERROR')
'''
