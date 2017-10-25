#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Programme de vérification des référentiels AMELi

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import json
import logging
import os.path

import helpers


class VersionDetector:
    """
    Détecteur de modification. Classe abstraite.
    Cette classe permet
    - de lire les données de la version précédente
    - de sauvegarder les données
    - une methode abstraite à implémenter pour déterminer si la version actuelle est nouvelle
    """
    VERSION_DATA_DIR = 'data'
    VERSION_FN_EXT = '.json'

    def __init__(self, ref):
        self.logger = logging.getLogger('detector')
        self.version = {"versions": []}
        self.ref = ref
        self.version_fn = os.path.join(VersionDetector.VERSION_DATA_DIR,
                                       '{}{}'.format(self.ref, VersionDetector.VERSION_FN_EXT))
        self.last = 0

    def load_previous_(self):
        """

        TODO: SUPPR
        :return:
        """
        if not os.path.exists(self.version_fn):
            self.logger.debug("No previous version. Init")
        else:
            self.version = helpers.load_json_config(self.version_fn)
            # get the max version of all records
            self.last = int(sorted(set(map(lambda x: x["version"], self.version["versions"])))[-1])

        self.logger.debug("Versions : {}".format(str(self.version)))

    def load_previous(self):
        """
        Lecture des données du précédent traitement et calcul du numéro de version
        :return: -
        """
        self.logger.debug("Loads previous version from {}".format(self.version_fn))
        self.version = helpers.load_json_config(self.version_fn)
        # calcule la version la plus recente : max
        self.last = int(sorted(set(map(lambda x: x["version"], self.version["versions"])))[-1])

        self.logger.debug("Versions : {}".format(str(self.version)))

    def save_current_versions(self):
        """
        Sauvegarde des données
        :return:
        """
        with open(self.version_fn, 'w') as fout:
            fout.write(json.dumps(self.version, sort_keys=True, indent=4))

    def new_version(self, version):
        """
        Emission d'une nouvelle version

        :param version: numéro de la version
        :return: données associées à la version
        """
        self.logger.info("Nouvelle version : {}".format(version))
        # add entry in version list
        self.version["versions"].insert(0, {"version": version["version"],
                                            "date": version["date"],
                                            "url": version["url"] if "url" in version else None,
                                            "files": version["files"] if "files" in version else None,
                                            "compl": version["compl"]})

    def is_newer(self, infos):
        return float(self.getCurrentVersion()) < float(infos["version"])

    def getCurrentVersion(self):
        return self.last

    def fetch_data(self):
        raise NotImplementedError("Abstract...")
