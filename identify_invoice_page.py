# Detects invoice page from a pdf or image.

import word_retriever as wr
import convert_pdf2image as pi

# from word_retriever import FeatureType

import os
import json

file_path = 'sample.pdf'  # give your pdf file path
out_folder = 'output'


# Detection from pdf
def detect_from_pdf():
    matching_loc_list = []
    invoice_detect_kwds = ['INVOICE', 'Invoice', 'Tax', 'TAX', 'Ship', 'Bill',
                           'Billing', 'Shipping', 'GSTIN', 'Registered',
                           'Regn', 'Buyer']
    threshhold_val = 4   # Num of keywords to match.
    # to clear out_folder before begining
    os.system('rm {}/*'.format(out_folder))
    val = pi.pdftoimage(file_path, out_folder)
    if val == 2:
        for file_name in os.listdir(out_folder):
            response, document, text = wr.data_retrieve(out_folder+'/'
                                                        + file_name)
            for i in invoice_detect_kwds:
                block_loc = wr.find_block_loc_from_word(document, i)
                if block_loc is None:
                    pass
                else:
                    # Appending all location values for check.
                    matching_loc_list.append(block_loc)

            if len(matching_loc_list) >= threshhold_val:
                return out_folder+'/'+file_name


invoice_file = detect_from_pdf()
# print(invoice_file)


def value_retrieve(ret_val):
    '''
    Method to retrieve certain values and store in a dict.
    '''
    try:
        data = ret_val[0]
        return data
    except:
        data = ''
        return data


def return_valid_data(inv_file):
    response, document, text = wr.data_retrieve(inv_file)
    # detection by block
    # bounds = wr.get_document_bounds(response, FeatureType.BLOCK, document)
    GST_values, MOB_nums, Mails = wr.reg_expn(text)
    check_data = GST_values
    check_data.append('Registered')
    # check_data.append('Office')
    # must_data.append('Regn')

    data_coll = []
    invalid_data = []
    data_dict1 = {}  # dictionary contaning final valid data
    avoid_data = ['Adani', 'ADANI', 'Billing', 'Shipping', 'Bill', 'Ship'
                  , 'Buyer']
    city_code_dict = {
                        '01': 'Jammu & Kashmir',
                        '02': 'Himachal Pradesh',
                        '03': 'Punjab',
                        '04': 'Chandigarh',
                        '05': 'Uttarakhand',
                        '06': 'Haryana',
                        '07': 'Delhi',
                        '08': 'Rajasthan',
                        '09': 'Uttar Pradesh',
                        '10': 'Bihar',
                        '11': 'Sikkim',
                        '12': 'Arunachal Pradesh',
                        '13': 'Nagaland',
                        '14': 'Manipur',
                        '15': 'Mizoram',
                        '16': 'Tripura',
                        '17': 'Meghalaya',
                        '18': 'Assam',
                        '19': 'West Bengal',
                        '20': 'Jharkhand',
                        '21': 'Orissa',
                        '22': 'Chhattisgarh',
                        '23': 'Madhya Pradesh',
                        '24': 'Gujarat',
                        '25': 'Daman & Diu',
                        '26': 'Dadra & Nagar Haveli',
                        '27': 'Maharashtra',
                        '28': 'Andhra Pradesh (Old)',
                        '29': 'Karnataka',
                        '30': 'Goa',
                        '31': 'Lakshadweep',
                        '32': 'Kerala',
                        '33': 'Tamil Nadu',
                        '34': 'Puducherry',
                        '35': 'Andaman & Nicobar Islands',
                        '36': 'Telengana',
                        '37': 'Andhra Pradesh (New)'
    }
    for value in check_data:
        # print(gst_value) # Debugging
        # state_code = gst_value[:2]
        # print(city_code_dict[state_code]) # Debugging
        location = wr.find_block_loc_from_word(document, value)
        # print(location) # Debugging
        # finding block wth containing word
        data = wr.text_within(document, location.vertices[0].x
                              , location.vertices[0].y, location.vertices[2].x
                              , location.vertices[2].y)
#        print('\n'+data) # Debugging
        data_coll.append(data)
    data_coll = set(data_coll)  # Done to avoid repetition
    # print(data_coll)
    for i in data_coll:
        for j in avoid_data:
            if i.find(j) != -1:
                invalid_data.append(i)
    invalid_data = set(invalid_data)  # avoid copies
    # removing invalid data from data_coll
    for data in invalid_data:
        data_coll.remove(data)
    for valid_data in data_coll:
        # print(valid_data)
        valid_GST_value, valid_MOB_num, valid_Mail = wr.reg_expn(valid_data)

        if value_retrieve(valid_GST_value) == '' and value_retrieve(valid_MOB_num) == '' and value_retrieve(valid_Mail) == '':
            pass
        else:
            data_dict1['GSTIN'] = value_retrieve(valid_GST_value)
            data_dict1['Mob Num'] = value_retrieve(valid_MOB_num)
            data_dict1['Email'] = value_retrieve(valid_Mail)
            try:
                data_dict1['Sate'] = city_code_dict[str(valid_GST_value[0])[:2]]
            except:
                data_dict1['Sate'] = ''

    return data_coll, data_dict1


def find_bal_data(data):
    '''
    Method to find balance data like Vendors Name , address etc.
    '''
    data_dict2 = {}
    vendor_idntfn_kwd = ['Limited', 'Ltd', 'LTD', 'Private', 'PRIVATE'
                         , 'INC', 'Inc']
    pos = 1
    for i in data:
        split_data = i.split(',')
        for j in split_data:
            for k in vendor_idntfn_kwd:
                if j.find(k) != -1:
                    end_lim = j.find(k) + len(k)
                    data_dict2['Vendor Name'] = j[:end_lim]
                    split_data.remove(j)
                    break
            data_dict2['Street'+str(pos)] = j
            pos += 1

    return data_dict2


def return_json(dict):
    '''
    Method to return a json file from a dictionary
    '''
    final_data = json.dumps(dict)
    return final_data


valid_data_coll, valid_data_dict1 = return_valid_data(invoice_file)
# print(valid_data_coll)  # Debugging
# print(valid_data_dict1)  # Debugging

valid_data_dict2 = find_bal_data(valid_data_coll)
# print(valid_data_dict2)  # Debugging

final_dict = {**valid_data_dict1, **valid_data_dict2} # Way to merge two dicts
# print(valid_data_dict1.update(valid_data_dict2))
# print(final_dict)

final_data = return_json(final_dict)
print(final_data)
