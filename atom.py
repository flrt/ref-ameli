#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Production d'un fichier ATOM XML

    Definition : https://tools.ietf.org/html/rfc4287

    Outil de validation : https://validator.w3.org/feed/

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import codecs
import datetime
import logging
import os.path
from xml.etree.ElementTree import SubElement

import content
import helpers


class Feed:
    """
        Création d'un fichier de flux RSS au format ATOM

    """
    AMELI_ATOM_FEED_DIR = "feeds"
    AMELI_ATOM_CONFIG_DIR = "conf"

    def __init__(self, ref, selfhref=''):
        """
        Constructeur du générateur

        Lien vers l'auto référence du flux : https://www.feedvalidator.org/docs/warning/MissingAtomSelfLink.html

        :param ref: référentiel concerné
        :param selfhref: HREF du flux XML une fois déployé pour son auto référence
        """
        self.logger = logging.getLogger('feed')
        self.ref = ref
        self.selhref = selfhref
        self.feed_config = {}
        self.load_config()
        self.feed_filename = os.path.join(Feed.AMELI_ATOM_FEED_DIR, self.feed_config["header"]["feedname"])
        self.update_date = datetime.datetime.now(datetime.timezone.utc).isoformat(sep='T')
        self.logger.debug("Feed : %s" % self.feed_filename)

    def load_config(self):
        """
        Chargement de la configuration du flux
        :return:
        """
        filename = os.path.join(Feed.AMELI_ATOM_CONFIG_DIR, "feed_config_{}.json".format(self.ref))
        self.logger.debug("Load config file : {}".format(filename))
        self.feed_config = helpers.load_json_config(filename)

    def generate(self, entries):
        """
        Génération du fichier XML Atom
        :param entries: listes des entrées du fichier
        :return: noeud XML du document Atom XML
        """
        self.logger.debug("Feed to XML : {} entries".format(len(entries)))

        root = content.xmlelt(None, "feed", None, {"xmlns": "http://www.w3.org/2005/Atom"})

        content.xmlelt(root, "id", self.feed_config["header"]["id"])
        content.xmlelt(root, "title", self.feed_config["header"]["title"])
        content.xmlelt(root, "subtitle", self.feed_config["header"]["subtitle"])
        content.xmlelt(root, "link", None,
                       {"href": self.feed_config["header"]["link"],
                        "rel": "related"})
        content.xmlelt(root, "link", None,
                       {"href": '{}{}'.format(self.selhref, self.feed_config["header"]["feedname"]),
                        "rel": "self"})

        content.xmlelt(root, "updated", self.update_date)
        author = SubElement(root, "author")
        content.xmlelt(author, "name", self.feed_config["header"]["author"]["name"])
        content.xmlelt(author, "email", self.feed_config["header"]["author"]["email"])

        content.xmlelt(root, "category", None,
                       {"term": self.feed_config["header"]["category"]})

        content.xmlelt(root, "generator", "app",
                       {"uri": "https://github.com/flrt",
                        "version": "1.0"})
        content.xmlelt(root, "rights", "CC BY-SA 3.0 FR")

        for entry in entries["versions"]:
            self.logger.debug("current entry : %s" % entry)

            xml_entry = content.xmlelt(root, "entry")
            content.xmlelt(xml_entry, "title", "{} {}".format(
                self.feed_config["entry"]["title_mask"], entry["version"]))

            if 'url' in entry and entry["url"]:
                content.xmlelt(xml_entry, "link", None,
                               {"href": entry["url"],
                                "rel": "related",
                                "type": self.mimetype(entry["url"])})

            if 'files' in entry and entry['files']:
                for fi in entry['files']:
                    content.xmlelt(xml_entry, "link", None,
                                   {"href": fi,
                                    "rel": "related",
                                    "type": self.mimetype(fi)})

            content.xmlelt(xml_entry, "id", "{}{}".format(
                self.feed_config["entry"]["urn_mask"], entry["version"]))

            content.make_xhtml(xml_entry, entry)

            content.xmlelt(xml_entry, "updated", entry["date"])

            content.xmlelt(xml_entry, "summary", "{} {} disponible".format(
                self.feed_config["entry"]["title_mask"], entry["version"]))

        return root

    @staticmethod
    def mimetype(link):
        """
        Detection du type mime en fonction de l'extension de l'URL
        :param link: URL du fichier
        :return: type mime associé. Type: str
        """
        mimetypes = {".zip": "application/zip", ".dbf": "application/dbase"}
        ext = link[link.rfind('.'):]
        if ext in mimetypes:
            return mimetypes[ext]
        else:
            return "application/octet-stream"

    def save(self, root):
        """
        Sauvegarde locale des données
        :param root: noeud XML
        :return: -
        """
        self.logger.info("Save {0}".format(self.feed_filename))
        encoding = 'utf-8'
        with codecs.open(self.feed_filename, "w", encoding) as fout:
            fout.write(content.xml2text(root, encoding))
