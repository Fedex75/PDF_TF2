import hashlib
import os
import glob
import traceback
from PyPDF2 import PdfReader

def text_between(line, before, after):
    '''Find string between two strings'''
    try:
        index_before = line.index(before)
        if after == "":
            return line[index_before + len(before):].strip()
        return line[index_before + len(before) : line.index(after, index_before + len(before))].strip()
    except Exception as _:
        print(f'substring not found ("{line}", "{before}", "{after}")')
        raise Exception from _

def file_hash(folder, file_name):
    '''Get file hash'''
    hasher = hashlib.sha256()
    with open(os.path.join(folder, file_name), 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

def find_unique_files(folder, file_list):
    '''Helper to find unique files in a folder'''
    hash_to_filename = {}
    unique_files = []

    for file_name in file_list:
        file_hash_value = file_hash(folder, file_name)
        if file_hash_value not in hash_to_filename:
            hash_to_filename[file_hash_value] = file_name
            unique_files.append(file_name)

    return unique_files

def get_unique_pdf_files(folder):
    '''Find unique files in a folder'''
    pdf_files = glob.glob(os.path.join(folder, '*.pdf'))
    pdf_file_names = [os.path.basename(pdf_file) for pdf_file in pdf_files]
    return find_unique_files(folder, pdf_file_names)

def csv_output(folder, file_names, out_file, header, process_function, increment_callback, finished_callback):
    '''Process files and output to new file'''
    csv = [header]
    id_pdf = 1
    for file_name in file_names:
        parcial = []
        try:
            parcial = process_function(folder + "/" + file_name, id_pdf)
        except Exception as _:
            print('Ocurrio un error procesando el pdf: ' + folder + "/" + file_name)
            print(traceback.format_exc())
            increment_callback(True)

        csv.extend(parcial)
        id_pdf += 1
        increment_callback(False)

    with open(os.path.join(folder, out_file), 'w', encoding='utf-8') as file:
        for line in csv:
            file.write(line + '\n')

    finished_callback()

def read_pdf(path):
    '''Create PdfReader from path'''
    return PdfReader(path)

def filter_empty_lines(lines):
    '''Remove empty lines from list'''
    return [s for s in lines if s.strip() != '']
