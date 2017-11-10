import helpers
import xlrd
import datetime
import json

data = helpers.load_json_config('data/lpp.json')

workbook = xlrd.open_workbook('down/LPP_TDB466.xls')
worksheet = workbook.sheet_by_index(0)
version = {}
for rownum in range(workbook.sheet_by_index(0).nrows):
    vals = worksheet.row_values(rownum)
    try:
        file_version = int(vals[0])
        try:
            val_4 = datetime.datetime(*xlrd.xldate_as_tuple(vals[4], workbook.datemode))
            version[file_version] = val_4
        except:
            print("ERR : %s" % vals[4])
            val_3 = datetime.datetime(*xlrd.xldate_as_tuple(vals[3], workbook.datemode))
            version[file_version] = val_3

    except ValueError:
        pass

for v in data["versions"]:
    vnum = int(v["version"])
    v["date"] = version[vnum].isoformat(sep='T')

with open('data/lpp2.json', 'w') as fout:
    fout.write(json.dumps(data, sort_keys=True, indent=4))
