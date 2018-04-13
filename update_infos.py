#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Mise a jour des details de la version 403

    python update_ucd_infos.py -v 403 -c data/ucd.json ucd
"""

import argparse
import watchdog
from easy_atom import helpers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", choices=['ucd'], help="referentiel : ucd")
    parser.add_argument("-v", "--version", help="""version a mettre a jour""")
    parser.add_argument("-c", "--conf", help="""fichier de configuration""")

    args = parser.parse_args()

    print(f'Ref : {args.ref}')
    print(f'version : {args.version}')
    print(f'fichier de config : {args.conf}')

    print(f'Lecture du fichier {args.conf}')

    data = helpers.load_json(args.conf)
    for data_vers in data['versions']:
        if data_vers['version']==args.version:
            html = watchdog.UCDWatchDog.format_html_compl(args.version, data_vers['files'])
            print(html)
            data_vers['html'] = html

    helpers.save_json(args.conf, data)
    print(f'Ecriture du fichier {args.conf}')


if __name__ == "__main__":
    main()
