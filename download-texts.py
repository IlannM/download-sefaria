# Ilan Mittelman

# note for the future: this script will break
# if github's raw url scheme changes, or if
# Sefaria changes the repo directory system.
# make sure to have a internet connection before running.
# ---- tested working as of January 31th, 2024 ----

# TODO
# - calculate bytes per second rate
# - zip the whole thing

import os
import time
import urllib.request
import shutil

def format_file(file, content):
    content = content.replace(chr(1475), '')
    content = content.replace(':', '')
    content = removeInfileMetadata(content)
    content = removeChaptersHeadings(content)
    removeNikkud(file, content)
    out_file = open('texts/'+file['path']+file['name'], 'w')
    out_file.write(content)
    out_file.close()

def removeNikkud(in_file, content):
    content = content.replace(chr(1470), ' ')
    for i in range(1456, 1479):
        content = content.replace(chr(i), '')
    # file = open('/stripped/'+file_name, 'w')
    out_file = open('texts/'+in_file['path']+'/stripped/'+in_file['name'], 'w')
    out_file.write(content)
    out_file.close()

# remove metadata at beginning of file
def removeInfileMetadata(content):
    for i in range(0,len(content)):
        if content[i] == 'C':
            content = content[i+11:]
            break
    return content

# remove Chapter X from the downloaded text
def removeChaptersHeadings(content):
    removed = True
    while removed:
        removed = False
        for i in range(0,len(content)):
            if content[i] == 'C':
                # print(ord(content[i+11]))
                magic_num = 11 # how many chars to remove
                if content[i+11] == '\n':
                    magic_num += 1
                
                # # i hate everything
                remove_newline = 0
                if content[i-3] == '\n':
                    print('yes')
                    remove_newline = 1
                # leave a newline between chapters to calculate at runtime
                # know the amount of chapters and verses
                content = content[:i-remove_newline] + content[i+magic_num:]
                removed = True
                break
    return content

books = {
'Torah': ['Genesis','Exodus','Leviticus','Numbers','Deuteronomy'],
'Prophets': [
    'Ezekiel','Habakkuk','Haggai','Hosea','I%20Kings',
    'I%20Samuel','II%20Kings','II%20Samuel', 'Isaiah','Jeremiah',
    'Joel','Jonah','Joshua','Judges','Malachi','Micah',
    'Nahum','Obadiah','Zechariah','Zephaniah',
]
}

start = time.time()

for path in books.keys():
    path = 'texts/'+path
    if not os.path.isdir(path):
        os.makedirs(path)
        os.makedirs(path+'/Targum/stripped')
        os.makedirs(path+'/stripped')

url = 'https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Tanakh/{}/{}/Hebrew/Tanach%20with%20Nikkud.txt'

bytes_recieved = 0

print('Downloading Scripture...')

for key, book in books.items():
    for i in book:
        download_url = url.format(key, i)
        i = i.replace('%20', ' ')
        new_file_name = {
            'path': key+'/',
            'name': i+'.txt'
        }

        # new_file_name = [key+'/', i+'.txt']
        # file_name = '{}/{}.txt'.format(key, i)
        with urllib.request.urlopen(download_url) as response:
            bytes_recieved += response.length
            format_file(new_file_name, response.read().decode('utf-8'))

print('Done.')

# download targum
targum = {
    'Torah': 'https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Tanakh/Targum/Onkelos/Torah/Onkelos%20{0}/Hebrew/Onkelos%20{0}.txt',
    'Prophets': 'https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/txt/Tanakh/Targum/Targum%20Jonathan/Prophets/Targum%20Jonathan%20on%20{}/Hebrew/Mikraot%20Gedolot.txt'
}

print('Downloading Targum...')
for key, book in books.items():
    for i in book:
        download_url = targum[key].format(i)
        i = i.replace('%20', ' ')
        new_file_name = {
            'path': key+'/Targum/',
            'name': i+'.txt'
        }
        # new_file_name = [ key+'/Targum', i+'.txt' ]
        # file_name = '{}/Targum/{}.txt'.format(key, i)
        with urllib.request.urlopen(download_url) as response:
            bytes_recieved += response.length
            format_file(new_file_name, response.read().decode('utf-8'))

print('Done.')

total_time = int(time.time() - start)

megabyte = 1048576
if bytes_recieved < megabyte:
    print('[-] Failed downloading files.')
readable_bytes = int(bytes_recieved / megabyte)
print('Successfully downloaded {} MB in {} seconds (# MB/s).'.format(readable_bytes, total_time))

print('Creating ZIP file...')
shutil.make_archive('Torah-Prophets', 'zip', 'texts')
print('Done.')
