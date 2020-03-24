# Detects invoice page from a pdf or image.
# Retrieves data from it and returns a json object

import word_retriever as wr
import convert_pdf2image as pi

# from word_retriever import FeatureType

import os
import json

file_path = 'sample.pdf'  # give your pdf file path
out_folder = 'output'  # output folder path where converted images are stored.


# Detection from pdf
def detect_from_pdf():
    '''
    Method to convert PDF into images and identify invoice page from it.
    Parameters: None
    Returns: Image file name with path.
    '''
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
    Parameters: Value from which data is to be retrieved
    Returns: Retrieve data.
    '''
    try:
        data = ret_val[0]
        return data
    except:
        data = ''
        return data


def return_valid_data(inv_file):
    '''
    Method to fetch valid data from the invoice page with required details.
    Parameters: image file with path
    Returns: Valid data, dictionary with gst,mob,mail etc. values.
    '''
    response, document, text = wr.data_retrieve(inv_file)
    # detection by block
    # bounds = wr.get_document_bounds(response, FeatureType.BLOCK, document)
    GST_values, MOB_nums, Mails = wr.reg_expn(text)
    check_data = GST_values
    check_val = ('Registered', 'Regd', 'Pvt', 'Ltd')  # Add items to be identified
    check_data.extend(check_val)

    data_coll = []
    invalid_data = []
    data_dict1 = {}  # dictionary contaning final valid data
    avoid_data = ['Adani', 'ADANI', 'Billing', 'Shipping', 'Bill', 'Ship'
                  , 'Buyer', 'From', 'To']
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
        # print(value)  # Debugging
        # state_code = gst_value[:2]
        # print(city_code_dict[state_code]) # Debugging
        location = wr.find_block_loc_from_word(document, value)
        if location is None:
            pass
        else:
            # print(location)  # Debugging
            # finding block wth containing word
            data = wr.text_within(document, location.vertices[0].x
                                  , location.vertices[0].y, location.vertices[2].x
                                  , location.vertices[2].y)
    #        print('\n'+data) # Debugging
            data_coll.append(data)
        data_coll = set(data_coll)  # Done to avoid repetition
        data_coll = list(data_coll)  # to list
        # print(data_coll)
        for i in data_coll:
            for j in avoid_data:
                if i.find(j) != -1:
                    invalid_data.append(i)
        invalid_data = set(invalid_data)  # avoid copies
        invalid_data = list(invalid_data)  # to list
        # removing invalid data from data_coll
        for data in invalid_data:
            try:
                data_coll.remove(data)
            except:
                pass
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


def find_vendor_name(data, vendor_kwd, typ=0):
    '''
    Method to find vendor name.
    Here, typ denotes the type of data. 0-string ... 1-list
    Parameters: source data, vendor identification keyword list, type of source data.
    Returns: Vendor Name, Item containing vndr_name
    '''
    list_data = []
    if typ == 0:
        list_data.append(data)
        data = list_data
    else:
        pass
    vndr_name = ''
    for i in data:
        for k in vendor_kwd:
            if i.find(k) != -1:
                end_lim = i.find(k) + len(k)
                vndr_name = i[:end_lim]
                return vndr_name, i
    # print('Vndr : '+vndr_name)  # Debugging
    return vndr_name, ''


def find_bal_data(data):
    '''
    Method to find balance data like Vendors Name , address etc.
    Parameters: source data
    Returns: dictionary with vndr_name, address etc.
    '''
    data_dict2 = {}
    vendor_idntfn_kwd = ['Limited', 'Ltd', 'LTD', 'Private', 'Pvt', 'PRIVATE'
                         , 'INC', 'Inc']
    pos = 1
    for i in data:
        gst_value, mob_num, mail = wr.reg_expn(i)
        data_dict2['Vendor Name'] = ''
        if value_retrieve(gst_value) == '' and value_retrieve(mob_num) == '' and value_retrieve(mail) == '':
            split_data = i.split(',')
            data_dict2['Vendor Name'], rem_data = find_vendor_name(split_data, vendor_idntfn_kwd, 1)
            # removing vendor name included item from list.
            if data_dict2['Vendor Name'] != '':
                try:
                    split_data.remove(rem_data)
                except:
                    pass
            for j in split_data:
                data_dict2['Street'+str(pos)] = j
                pos += 1
        else:
            if data_dict2['Vendor Name'] == '':
                data_dict2['Vendor Name'], nonuse_data = find_vendor_name(i, vendor_idntfn_kwd, 0)
    return data_dict2


def return_json(dict):
    '''
    Method to return a json file from a dictionary
    Parameters: Merged dictionary
    Returns: Converted json object.
    '''
    final_data = json.dumps(dict)
    return final_data


# Retrieving Valid data as a list and Valid ditionary which contains gstin, mob, mail etc.
valid_data_coll, valid_data_dict1 = return_valid_data(invoice_file)
# print(valid_data_coll)  # Debugging
# print(valid_data_dict1)  # Debugging

valid_data_dict2 = find_bal_data(valid_data_coll)
# print(valid_data_dict2)  # Debugging

final_dict = {**valid_data_dict1, **valid_data_dict2}  # Way to merge two dicts
# print(valid_data_dict1.update(valid_data_dict2))
# print(final_dict)

# Conversion to json object
final_data = return_json(final_dict)
print(final_data)
