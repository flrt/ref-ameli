#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import logging
import os.path
import shutil
from ftplib import FTP

import mailer
import requests

import content
import helpers


class Action:
    """
    Abstract class
    Base des actions
    """

    def __init__(self, conf_filename=None, conf=None):
        """
        Constructeur initialisant l'action avec des données de configuration

        :param conf_filename: Fichier contenant les paramètres de configuration
        :param conf: Paramètres directement fournis dans 1 dictionnaire
        """
        self.conf = conf
        self.conf_filename = conf_filename
        self.logger = logging.getLogger('action')

        self.logger.debug("Fichier de configuration : %s" % self.conf_filename)
        if conf_filename:
            self.load_config()

    def load_config(self):
        """
        Lecture des données de configuration. Les donnees sont accessibles dans conf
        :return: -
        """
        if self.conf_filename and os.path.exists(self.conf_filename):
            self.logger.debug("Load configuration file = {}".format(self.conf_filename))
            self.conf = helpers.load_json_config(self.conf_filename)

    def process(self, infos):
        raise Exception("Abstract method")


class SendMailAction(Action):
    """
    Action : envoi de mail
    """

    def __init__(self, conf_filename=None, conf=None, nomenclature=None):
        Action.__init__(self, conf_filename=conf_filename, conf=conf)
        self.nomen = nomenclature if nomenclature is not None else ''
        self.logger.debug("Mail configuration : %s" % self.conf)

    def process(self, infos):
        """
        En prenant les informations dans la configuration fournie, un mail est envoyé en se basant
        sur les informations contenues dans le paramètre
        :param infos: données à envoyer par mail
        :return: -
        """
        self.logger.debug("Send Mail notification, infos = {}".format(infos))
        if self.conf:
            message = mailer.Message(From=self.conf['from'], To=self.conf['to'], charset="utf-8")
            message.Subject = "{} {}".format(self.conf['subject'], self.nomen.upper())

            message.Html = content.xml2text(content.make_xhtml(root=None, entry=infos), 'utf-8')
            sender = mailer.Mailer(host=self.conf['server'], port=self.conf['port'],
                                   usr=self.conf['user'], pwd=self.conf['passwd'],
                                   use_ssl=self.conf['usessl'])
            sender.send(message)
            self.logger.debug("Mail sent to {}".format(self.conf['to']))


class DownloadAction(Action):
    """
    Action de téléchargement de fichiers définis par des URL
    """

    def download(self, url):
        return self.download_url(self.conf['download_dir'], url)

    @staticmethod
    def download_url(download_dir, url):
        if download_dir and not os.path.exists(download_dir):
            os.makedirs(download_dir)

        local_filename = os.path.join(download_dir, url.split('/')[-1])

        req = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(req.raw, f)

        return os.path.abspath(local_filename)

    def process(self, infos):
        """
        Télécharge en local les fichiers désignés par des URL dans les données info.
        Les fichiers peuvent être désignés par la clé <url> ou par la clé <files>

        Exemple :
        infos = {'type': 'CCAM',
        'version': 49.0,
        'date': '2017-10-21T08:14:06.351015+00:00',
        'url': None,
        'files': [
        'https://www.ameli.fr/fileadmin/user_upload/documents/CCAM04900_DBF_PART1.zip',
        'https://www.ameli.fr/fileadmin/user_upload/documents/CCAM04900_DBF_PART2.zip',
        'https://www.ameli.fr/fileadmin/user_upload/documents/CCAM04900_DBF_PART3.zip']}

        :param infos: dictionnaire contenant les informations sur les données à télécharger
        :return: Liste des fichiers locaux telechargés, type: List
        """
        files = []

        if self.conf and self.conf['download']:
            self.logger.info("Téléchargement des fichiers...")
            if infos["url"]:
                fn = self.download(infos["url"])
                files.append(fn)
            if len(infos["files"]):
                for f in infos["files"]:
                    fn = self.download(f)
                    files.append(fn)

        return files


class UploadAction(Action):
    """
    Action de téléchargement sur un site FTP de fichiers
    Les données de connexion au serveur FTP sont fournies via les données de configuration
    Voir le constructeur.
    """

    def process(self, infos):
        """
        Télécharge tous les fichier sur le site FTP distant
        :param infos: Liste des fichiers à télécharger : type: List
        :return: -
        """

        with FTP(self.conf["server"], self.conf["user"], self.conf["passwd"]) as ftp_cnx:
            ftp_cnx.cwd(self.conf["remotedir"])
            for filename in infos:
                if os.path.exists(filename)
                    self.logger.debug("Upload file : %s -> %s" % (filename, os.path.basename(filename)))
                    fh = open(filename, 'rb')  # file to send
                    ftp_cnx.storbinary('STOR %s' % os.path.basename(filename), fh)  # send the file
                    fh.close()  # close file and FTP
                else:
                    self.logger.warn("File %s not found" % filename)
