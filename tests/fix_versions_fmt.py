from easy_atom import helpers
fn = "data/lpp.json"
fn2 = "data/lpp2.json"

data = helpers.load_json(fn)

for rec in data['versions']:
    v=rec['version']
    rec['title']=f'Nomenclature LPP Version {v}'
    rec['id']=f'urn:ameli:lpp:{v}'
    rec['type']='LPP'
    rec['summary']=f'Version {v} disponible'
    rec['url']=None

helpers.save_json(fn2, data)