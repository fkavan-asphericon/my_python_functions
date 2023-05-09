import deepl
import re
import os
from dotmap import DotMap

from authkey import auth_key

translator = deepl.Translator(auth_key)
default_language = 'CS'


def remove_excessive_elements(lines):
    num_replacements = 0
    replacements = []
    newlines = []
    for line in lines:
        newline = line
        patterns = [r' {2,}', r'<[^<]+?>', r'\\n', r'&[a-z]{1,4};[a-z]{,4};?']
        for pattern in patterns:
            finds = re.findall(pattern, newline)
            line_split = re.split(pattern, newline)
            newline = line_split[0]
            for k in range(len(finds)):
                newline += '{%d}' % num_replacements + line_split[k+1]
                replacements.append(finds[k])
                num_replacements += 1
        newlines.append(newline)
    return newlines, replacements

def add_excessive_elements(lines,replacements):
    newlines = []
    for line in lines:
        indices = [int(k[1:-1]) for k in re.findall(r'\{\d+\}', line)]
        line_split = re.split(r'\{\d+\}', line)
        newline = line_split[0]
        for k in range(len(indices)):
            newline += replacements[indices[k]] + line_split[k+1]
        newlines.append(newline)
    return newlines

def translate_po_file(filepath, language=default_language, max_num_translations = 150):
    folder = os.path.dirname(filepath);
    try:
        all_completed = True
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            translations_list = []
            replacement_list = []
            num_translations = 0
            last_msgid = 0
            num_lines = len(lines)
            for linenum in range(num_lines):
                if num_translations > max_num_translations:
                    all_completed = False
                    break
                line = lines[linenum]
                if line.startswith('msgid "'):
                    last_msgid = linenum
                    continue
                if line == 'msgstr ""\n' and (linenum+1 >= num_lines or lines[linenum+1] == '\n' or not lines[linenum+1]):
                    to_translate = [re.findall(r'".*"',lines[k])[0][1:-1] for k in range(last_msgid,linenum)]
                    cleaned,replacements = remove_excessive_elements(to_translate)
                    cleaned = '\n'.join(cleaned)
                    translations_list.append(cleaned)
                    replacement_list.append(replacements)
                    lines[linenum] = '{autotranslation,%d' % num_translations
                    num_translations += 1
        
        translations = translator.translate_text(translations_list, target_lang=language);

        for linenum in range(num_lines):
            line = lines[linenum]
            if line.startswith('{autotranslation,'):
                trans_num = int(line.split(',')[1])
                translation_split = translations[trans_num].text.split('\n')
                translation_split = ['"%s"\n' % k for k in translation_split]
                translation_split[0] = 'msgstr ' + translation_split[0]
                translation_split = add_excessive_elements(translation_split, replacement_list[trans_num])
                lines[linenum] = translation_split


        final_lines = []
        for line in lines:
            if isinstance(line, str):
                final_lines.append(line)
            else:
                final_lines.extend(line)

        newfilepath = folder + '\\' + language.lower() + '_translation_deepl.po'

        with open(newfilepath, 'w+', encoding='utf-8') as file:
            for line in final_lines:
                file.write(line)
        return DotMap({
            'error': False,
            'num_translations': num_translations,
            'all_completed': all_completed,
            'created_file': newfilepath,
        })
    except Exception as e:
        return DotMap({
            'error': True,
            'error_code': str(e)
        })

print('g')
# translate_po_file(r'c:\Downloads\asphericon_project_addon2.po', language='CS', max_num_translations = 150)