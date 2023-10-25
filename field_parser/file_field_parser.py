import sys
sys.path.append(r'c:\Developer\mpf\field_parser')
import os
import field_parser as FieldParser

filepath = r'c:\Developer\ODOO16\odoo-obs\26House'

fl = []
for root, dirs, files in os.walk(filepath):
    for file in files:
        if file.endswith(".py") and 'pohoda_xsd' not in root and 'tests' not in root:
             fl.append(os.path.join(root, file))


def missing_string_sort(stack):
    parsed_field = FieldParser.SingleParser(stack)
    new_parsed_fiel = FieldParser.FieldReformat(parsed_field)
    new_parsed_fiel.insert(FieldParser.Parameter('string',parsed_field.AutoFieldDescription()))
    new_parsed_field = FieldParser.FieldReformat(new_parsed_fiel)
    short = len(new_parsed_field) < 90
    return new_parsed_field.dump(short=short, leading_spaces=True) + '\n'

for fpath in fl:
    print(fpath)
    with open(fpath,'r+',encoding='utf8') as file:
        iterator = file.readlines()
        new_file_lines = FieldParser.MultiParse(iterator, changer=missing_string_sort)
    with open(fpath,'w+',encoding='utf8') as file:
        file.write(new_file_lines)
        # with open(fpath+'n', 'w+') as newfile:

print('Done')
