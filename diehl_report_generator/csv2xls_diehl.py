import csv
import re
from configparser import ConfigParser
from pathlib import Path
from openpyxl import load_workbook
import re
from datetime import datetime

CELL_RE = re.compile(r"^[A-Za-z]{1,3}\d+$")
cfg = ConfigParser() 
HERE = Path(__file__).resolve()

# Složka, kde soubor leží
ROOT = HERE.parent

inifile = r'config.ini'
cfg.read(Path(ROOT, inifile), encoding='utf-8')

xls_template = cfg.get('base', 'xls_template', fallback=None)
header_names = [x.strip() for x in cfg.get('base', 'headers', fallback='').split(',')]
num_header_names = len(header_names)

def open_corss_csv(file_path = r'c:\Developer\mpf\diehl_report_generator\sample.csv'):
    return list(csv.reader(open(file_path, encoding='utf-8'), delimiter=';'))

def parse_corss_data(corss_csv_data = open_corss_csv()):
    raw_headers = corss_csv_data[0:num_header_names]

    for k in range(num_header_names):
        assert raw_headers[k][0] == header_names[k]

    parsed_headers = []

    for m in range(1, len(raw_headers[0])):
        parsed_headers.append({header_names[k]: raw_headers[k][m] for k in range(num_header_names)})

    raw_data = corss_csv_data[num_header_names:]
    parsed_rows = {}
    for row in raw_data:
        parsed_rows[int(row[0])] = row[1:]

    return parsed_headers, parsed_rows

def find_header(headers, verify_fn = None, **filters):
    matches = []
    match_h = []
    def default_verify(needle, haystack):
        if needle[0] == needle[-1] == '/':
            return bool(re.findall(needle[1:-1], haystack))
        else:
            return needle == haystack
    
    verify_fn = verify_fn or default_verify

    for i, header in enumerate(headers):
        if all(verify_fn(value, header.get(key)) for key, value in filters.items()):
            matches.append(i)
            match_h.append(header)
    return matches, match_h

def get_mappings(cfg, headers):
    mappings = {}
    header_names = headers[0].keys()
    for section in cfg.sections():
        if section.startswith('mapping '):
            mapping_name = section[len('mapping '):]
            column = cfg.get(section, 'column', fallback=None)
            filters = {h: cfg.get(section, h) for h in header_names if cfg.has_option(section, h)}
            if not column:
                continue
            matches, mh = find_header(headers, verify_fn=None, **filters)
            if not matches:
                print(f"No matches found for {mapping_name} in headers")
                continue
            if len(matches) > 1:
                print(f"Multiple matches found for {mapping_name} in headers: {mh}")
                continue
            mappings[column] = matches[0]
    return mappings

def map_data(cfg, headers, data):
    mapped_data = []
    for row in data:
        mapped_row = {}
        for key, value in cfg.items('mapping Irregularity'):
            if key in headers:
                mapped_row[value] = row[headers.index(key)]
        mapped_data.append(mapped_row)
    return mapped_data

def map_data(mappings, data):
    mapped_data = {}
    row_number = cfg.getint('base', 'first_row', fallback=1)
    step = cfg.getint('base', 'rowspacing', fallback=1)
    for row in data:
        for key, value in mappings.items():
            mapped_data[f'{key}{row_number}'] = data[row][value]
        row_number += step
    return mapped_data


def coerce_number(s: str):
    """
    Try to convert a string like '6.004' or '52' to a number.
    Keeps strings (e.g., IDs like '20212') as text if leading zero risk or non-numeric.
    Adjust the heuristic as needed.
    """
    if not isinstance(s, str):
        return s
    t = s.strip().replace(",", ".")  # tolerate comma decimals
    # Only pure numeric tokens get cast
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        # Heuristic: treat 5+ digit integers as IDs (keep as text)
        if "." not in t and len(t) >= 5:
            return s
        return float(t) if "." in t else int(t)
    return s

def write_dict_to_xlsm(
    cell_map: dict,
    template_path: str,
    output_path: str = None,
    sheet_name: str = None,
    cast_numbers: bool = True,
):
    """
    Writes values to cells in an .xlsm template and saves as a new file.
    - cell_map: {'B13': '20212', 'I13': '0.4', ...}
    - template_path: path to existing .xlsm with macros
    - output_path: where to save; if None, auto-names next to template
    - sheet_name: target sheet; if None, uses active sheet
    - cast_numbers: convert numeric-looking strings to numbers
    """
    wb = load_workbook(template_path, keep_vba=True)  # preserves macros
    ws = wb[sheet_name] if sheet_name else wb.active

    for addr, val in cell_map.items():
        if not CELL_RE.match(addr):
            # skip keys that aren't valid cell addresses
            continue
        ws[addr] = coerce_number(val) if cast_numbers else val

    if output_path is None:
        p = Path(template_path)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = str(p.with_name(f"{p.stem}_filled_{stamp}{p.suffix}"))

    wb.save(output_path)
    return output_path

headers, data = parse_corss_data()
mappings = get_mappings(cfg, headers)
mapped_data = map_data(mappings, data)

output_file = write_dict_to_xlsm(mapped_data, Path(ROOT, cfg.getint('base', 'xls_template', fallback="diehl_template.xlsm")), sheet_name=cfg.get('base', 'xls_sheet', fallback="Frontlinse"))
print("Saved to:", output_file)
pass