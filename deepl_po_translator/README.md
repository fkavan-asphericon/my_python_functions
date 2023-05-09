# DeepL po translator
- Script developed to automatically create po files translations
- Translates files using DeepL API and python DeepL Library
- created by Frantisek Kavan

## Install
- Create user account and insert API key into deepl_po_translator/authkey.py
- It should look like `auth_key = "57b2c450-21e7-8581-41e0-0ef1245eca23:fx"`
- Check for requirements `pip install -r requirements.txt`
- Add to _sys.path_ using `sys.path.append('/path/to/repository')`
- Import po translator `import deepl_po_translator`

## Usage
`deepl_po_translator.translate_po_file(filepath, language=default_language, max_num_translations = 150)`

- filepath - full or relative path to .po file
- language - two character language code, see DeepL docs https://github.com/DeepLcom/deepl-python
- max_num_translations - limit number of translations in po file in one run
- you can also use .bat file