import translation_deepl
import os
import sys
import pyperclip

# print(sys.argv)
print('+---------------------------------------+')
print('| PO language translator based on DeepL |')
print('+---------------------------------------+')
print('')
print('version 0.1')
print('Developed by Frantisek Kavan')
print('')
if(len(sys.argv) < 2):
    filepath = input('Specify file to translate: ')
    print('')
else:
    filepath = sys.argv[1]

print('Translated file :')
print(filepath)
print('')

if not os.path.isfile(filepath):
    print('This is not a valid file')
    exit()

print('Select the language you want to translate to :')
print('Use two digit code like (de,cs,en)')
print('--- or type ---')
print('(1) for Czech (default)')
print('(2) for German')
print('(3) for English')
print('')
lang = input('Your choice: ')
lang = lang.strip()
if not lang or lang == '1':
    lang = 'CS'
elif lang == '2':
    lang = 'DE'
elif lang == '3':
    lang = 'EN'

print('Selected language: ' + lang)
print('')
result = translation_deepl.translate_po_file(filepath, lang)
if(not result.error):
    print('Translation complete')
    print('Translation file ' + result.created_file + ' was created')
    print('Number of new translations: %d' % result.num_translations)
else:
    print('There was an error with translation')
    print(result.error_code)
