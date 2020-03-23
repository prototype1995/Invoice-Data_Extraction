#### Detects invoice page from a pdf or image.

import word_retriever as wr
import convert_pdf2image as pi

from word_retriever import FeatureType

import os
import json

file = 'sample.pdf' # give your pdf file name
file_path = './sample.pdf'# give your pdf file path
out_folder = 'output'


# Detection from pdf
def detect_from_pdf():
    matching_loc_list = []
    invoice_detect_kwds = ['INVOICE', 'Invoice', 'Tax', 'TAX', 'Ship', 'Bill', 'Billing', 'Shipping', 'GSTIN', 'Registered', 'Regn', 'Buyer']
    threshhold_val = 4 # Num of keywords to match.
    os.system('rm {}/*'.format(out_folder)) # to clear out_folder before begining
    val = pi.pdftoimage(file_path, out_folder, file)
    if val==2:
        for file_name in os.listdir(out_folder):
            response, document, text = wr.data_retrieve(out_folder+'/'+file_name)
            for i in invoice_detect_kwds:
                block_loc = wr.find_block_loc_from_word(document, i)
                if block_loc is None:
                    pass
                else:
                    matching_loc_list.append(block_loc) # Appending all location values for check.

            if len(matching_loc_list)>=threshhold_val:
                return out_folder+'/'+file_name

invoice_file = detect_from_pdf()
#print(invoice_file)

def return_valid_data(inv_file):
    response, document,text = wr.data_retrieve(inv_file)
    bounds=wr.get_document_bounds(response, FeatureType.BLOCK, document) # detection by block
    GST_values, MOB_nums, Mails = wr.reg_expn(text)

    data_coll = []
    invalid_data = []
    data_dict = {} # dictionary contaning final valid data
    avoid_data = ['Adani', 'ADANI', 'Billing', 'Shipping', 'Bill', 'Ship', 'Buyer']
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
#        state_code = gst_value[:2]
#        print(city_code_dict[state_code]) # Debugging
        location=wr.find_block_loc_from_word(document,gst_value)
        #print(location) # Debugging
        # finding block wth containing word
        data = wr.text_within(document, location.vertices[0].x, location.vertices[0].y, location.vertices[2].x,location.vertices[2].y)
#        print('\n'+data) # Debugging
        data_coll.append(data)
    data_coll = set(data_coll) # Done to avoid repetition
    print(data_coll)
    for i in data_coll:
        for j in avoid_data:
            if i.find(j)!=-1:
                invalid_data.append(i)
    invalid_data = set(invalid_data) # avoid copies
    # removing invalid data from data_coll
    for data in invalid_data:
        data_coll.remove(data)
    for valid_data in data_coll:
#        print(valid_data)
        valid_GST_value, valid_MOB_num, valid_Mail = wr.reg_expn(valid_data)
        try:
            data_dict['GSTIN'] = valid_GST_value[0]
        except:
            data_dict['GSTIN'] = ''
        try:
            data_dict['Mob Num'] = valid_MOB_num[0]
        except:
            data_dict['Mob Num'] = ''
        try:
            data_dict['Email'] = valid_Mail[0]
        except:
            data_dict['Email'] = ''
        try:
            data_dict['State'] = city_code_dict[str(valid_GST_value[0][:2])]
        except:
            data_dict['State'] = ''
    return data_coll, data_dict

valid_data_coll = []
valid_data_coll, valid_data_dict = return_valid_data(invoice_file)
print(valid_data_coll) # Debugging
print(valid_data_dict) # Debugging


## Remaining to be done.
'''
def return_json_data(data):
    global data_dict
    data_Dict = {}
    count = 0
    sep_content_comma = data.split(',')
#    print(sep_content) # Debugging
    for i in sep_content_comma:
#        sep_cntent_space = i.split(' ')
#        for j in sep_cntent_space:
        for k in valid_data_dict.values():
            if i.find(k)==-1:
                count+=1
                data_Dict['Line'+str(count)] = i
    data_dict = data_Dict


for each_data in valid_data_coll:
    return_json_data(each_data)

#print(data_dict)

json_data = json.dumps(data_dict)

print(json_data)
'''
