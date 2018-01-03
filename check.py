#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Programme de vérification des référentiels AMELI

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import argparse
import logging
import sys

import helpers
import watchdog


def main():
    parser = argparse.ArgumentParser(epilog='''
    (*) Lien sur le lien autoréférencé dans ATOM : 
    https://www.feedvalidator.org/docs/warning/MissingAtomSelfLink.html ''')

    parser.add_argument("ref", choices=['ucd', 'lpp', 'ccam', 'nabm'], help="referentiel : ucd | lpp | ccam | nabm")
    parser.add_argument("-a", "--action", action="append",
                        choices=['feed', 'download'],
                        help="""
                        action disponible : <feed> -> produit un fichiers de syndication ATOM, 
                        <download> -> télécharge les fichiers""")
    parser.add_argument("--feedbase",
                        help="URL de base des flux atom, utilisés dans le flux ATOM pour s'autoréférencer (*)")
    parser.add_argument("--feedftp", help="configuration FTP pour upload du flux ATOM, format JSON")
    parser.add_argument("--dataftp", help="configuration FTP pour upload des données, format JSON")
    parser.add_argument("--mail", help="configuration Mail pour envoyer une notification, format JSON")
    parser.add_argument("--backupdir", help="Répertoire de sauvegarde des pages html")
    parser.add_argument("--downdir", help="Répertoire de téléchargements des fichiers de données")

    args = parser.parse_args()

    if not args.action:
        sys.stderr.write("## Erreur >> Aucune action définie !\n\n")
        parser.print_help(sys.stderr)
        sys.exit(1)

    feed_conf = {
        'ftp_config': args.feedftp,
        'feed_base': args.feedbase
    }
    data_conf = {
        'download': 'download' in args.action,
        'ftp_config': args.dataftp,
        'backup_dir': args.backupdir if args.backupdir else 'backup',
        'download_dir': args.downdir if args.downdir else 'down'
    }

    wd_class = {"ucd": watchdog.UCDWatchDog,
                "lpp": watchdog.LPPWatchDog,
                "ccam": watchdog.CCAMWatchDog,
                "nabm": watchdog.NABMWatchDog}

    instance = wd_class[args.ref](nomen=args.ref,
                                  feed_conf=feed_conf,
                                  data_conf=data_conf,
                                  mail_conf=args.mail)
    instance.process()


if __name__ == "__main__":
    loggers = helpers.stdout_logger(['ccam_wd', 'lpp_wd', 'ucd_wd', 'nabm_wd', 'feed', 'action'], logging.INFO)
    main()
