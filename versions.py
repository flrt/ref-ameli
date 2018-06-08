#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Programme de vérification des référentiels AMELi

"""
__author__ = 'Frederic Laurent'
__version__ = "1.1"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import json
import logging
import os.path

from easy_atom import helpers


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
            self.version = helpers.load_json(self.version_fn)
            # get the max version of all records
            self.last = int(sorted(set(map(lambda x: x["version"], self.version["versions"])))[-1])

        self.logger.debug("Versions : {}".format(str(self.version)))

    def load_previous(self):
        """
        Lecture des données du précédent traitement et calcul du numéro de version
        :return: -
        """
        self.logger.debug("Loads previous version from {}".format(self.version_fn))
        self.version = helpers.load_json(self.version_fn)
        # calcule la version la plus recente : max
        self.last = int(sorted(set(map(lambda x: x["version"], self.version["versions"])))[-1])

        self.logger.info("Derniere version traitee : {}".format(self.last))

    def save_current_versions(self):
        """
        Sauvegarde des données
        :return:
        """
        with open(self.version_fn, 'w') as fout:
            fout.write(json.dumps(self.version, sort_keys=True, indent=4))

    def new_version(self, infos):
        """
        Emission d'une nouvelle version

        :param version: numéro de la version
        :return: données associées à la version
        """
        self.logger.info(f"Nouvelle version : {infos}")
        # add entry in version list
        self.version["versions"].insert(0, infos)

    def is_newer(self, infos):
        return float(self.get_current_version()) < float(infos["version"])

    def in_progress_status_changed(self, infos):
        self.logger.debug(f"Version {infos['version']}, statut={infos['available']}")
        if "available" in infos and infos["available"]==False:
            return False
        
        # version courante totalement disponible
        _v = float(infos["version"])
        # recuperation des enregistrements ayant la meme version
        _vv = list(filter(lambda x: x['version'], self.version['versions']))

        _same_version = list(filter(
                lambda x: "version" in x and float(x["version"])==_v, self.version['versions']))
        self.logger.debug(f"Version actuelle {_v}, nb d'enregistrement dans l'historique {len(_same_version)}")
        # recuperation des enregistrements qui sont en non dispo
        _in_progress = list(filter(lambda x: "available" in x and x["available"]==False, _same_version))

        # si le nombre d'enregistrement en cours == nombre total -> il n'y avait pas de version disponible
        status_changed = len(_same_version)!=len(_in_progress)
        self.logger.debug(f"Changement status ? {status_changed}")

        return status_changed


    def get_current_version(self):
        return self.last

    def fetch_data(self):
        raise NotImplementedError("Abstract...")
