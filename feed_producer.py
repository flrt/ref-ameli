#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    

    python feed_producer
"""

import argparse
from easy_atom import atom
from easy_atom import helpers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", choices=['ucd','lpp', 'nabm', 'ccam'], 
                        help="referentiel : ucd, lpp, nabm, ccam")
    parser.add_argument("-s", "--selfhref", help="""Self Href""")

    args = parser.parse_args()

    print(f'Ref : {args.ref}')
    json_file = f'data/{args.ref}.json'
    datajs = helpers.load_json(json_file)
    
    f = atom.Feed(ref=args.ref, selfhref=args.selfhref)
    feed = f.generate(datajs['versions'])
    f.save(feed)
    f.rss2()


if __name__ == "__main__":
    main()
