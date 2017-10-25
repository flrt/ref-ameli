#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Analyse des pages sur le site ameli pour détecter les nouvelles versions.

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import datetime
import logging
import os.path
import re

import requests
import xlrd
from bs4 import BeautifulSoup

import action
import atom
import versions


class WatchDog(versions.VersionDetector):
    CONF_DATA_DIR = 'conf'

    """
    Analyse le changement et enchaine les actions necessaires
    """

    def __init__(self, nomen, feed_conf=None, data_conf=None, mail_conf=None):
        versions.VersionDetector.__init__(self, nomen)
        self.logger = logging.getLogger('%s_wd' % nomen)
        self.nomen = nomen
        self.feed_conf = feed_conf
        self.data_conf = data_conf
        self.mail_conf = mail_conf

        self.logger.debug("Feed configuration : %s" % self.feed_conf)
        self.logger.debug("Data configuration : %s" % self.data_conf)
        self.logger.debug("Mail configuration : %s" % self.mail_conf)

    def process(self):
        self.load_previous()
        infos = self.fetch_data()

        if infos and self.is_newer(infos):
            self.new_version(infos)
            self.save_current_versions()

            if self.feed_conf:
                # https://validator.w3.org/feed/docs/warning/RelativeSelf.html

                updatedfeed = atom.Feed(self.nomen, selfhref=self.feed_conf['feed_base'])
                feed = updatedfeed.generate(self.version)
                updatedfeed.save(feed)

                if self.feed_conf['ftp_config']:
                    act = action.UploadAction(conf_filename=self.feed_conf['ftp_config'])
                    act.process([updatedfeed.feed_filename])

            files = []
            # telechargement des fichiers si configurés
            if self.data_conf and self.data_conf['download']:
                act = action.DownloadAction(conf=self.data_conf)
                files = act.process(infos)

            # si les fichiers ont été téléchargés et qu'il faut les envoyer sur 1 serveur FTP
            if self.data_conf['ftp_config']:
                act = action.UploadAction(conf_filename=self.data_conf['ftp_config'])
                act.process(files)

            # s'il faut notifier par mail la nouvelle version
            if self.mail_conf:
                act = action.SendMailAction(conf_filename=self.mail_conf, nomenclature=self.nomen)
                try:
                    act.process(infos)
                except Exception as error:
                    self.logger.error("Erreur mailer : {} {}".format(type(error), error))

    def save_srcfile(self, content):
        """
        Sauvegarde des données source : page html ameli
        :param content: page html
        :return: -
        """
        if self.data_conf['backup_dir']:
            if not os.path.exists(self.data_conf['backup_dir']):
                os.makedirs(self.data_conf['backup_dir'])

            dn = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
            fn = os.path.join(self.data_conf['backups_dir'], "{0}_{1}.html".format(dn, self.nomen.upper()))

            with open(fn, "w") as fout:
                fout.write(content)


class UCDWatchDog(WatchDog):
    def fetch_data(self):
        self.logger.info("Fetch data... Current version  > %d ", self.getCurrentVersion())

        baseurl = 'http://www.codage.ext.cnamts.fr'
        url2check = '/codif/bdm_it/index_tele_ucd.php'

        infos = {'type': 'UCD', 'version': self.getCurrentVersion(),
                 'date': datetime.datetime.now(datetime.timezone.utc).isoformat(sep='T'),
                 'url': None,
                 'files': [], 'compl': None}

        regexdata = re.compile(
            r'.*?(ucd_total|ucd_histo_prix|retro_histo_taux|retro_histo_cout_sup)_(\d+)_(\d+)\.dbf')
        rcheck = requests.get("%s%s" % (baseurl, url2check))

        # /f_mediam/fo/bdm_it/ucd_total_00276_20150515.dbf
        # /f_mediam/fo/bdm_it/ucd_maj_00276_20150515.dbf
        # /f_mediam/fo/bdm_it/ucd_histo_prix_00276_20150515.dbf
        # /f_mediam/fo/bdm_it/retro_histo_taux_00276_20150515.dbf
        # /f_mediam/fo/bdm_it/retro_histo_cout_sup_00276_20150515.dbf

        if rcheck.status_code == 200:
            # parse du contenu
            soup = BeautifulSoup(rcheck.text, "html5lib")

            # sauvegarde
            self.save_srcfile(rcheck.text)

            links = list(filter(lambda x: x.get('href'), soup.find_all('a')))
            dbf_list = list(filter(lambda x: x.get('href').endswith('.dbf'), links))

            for link in dbf_list:
                # recuperation des liens vers les document dbf

                resregex = regexdata.match(link.get('href'))
                if resregex:
                    # recuperation du numero de version dans le nom de
                    # fichier
                    self.logger.debug(resregex.groups())
                    infos["version"] = str(int(resregex.group(2)))
                    infos["files"].append('%s%s' % (baseurl, link.get('href')))

        else:
            self.logger.error(
                "Probleme de recuperation du document UCD / ameli [%s]", rcheck.status_code)
            self.logger.error("URL : %s%s", baseurl, url2check)

        return infos


class LPPWatchDog(WatchDog):
    """
    Referentiel LPP

    Données : http://www.codage.ext.cnamts.fr/f_mediam/fo/tips/LPP466.zip
    Infos : http://www.codage.ext.cnamts.fr/f_mediam/fo/tips/LPP_TDB466.xls

    """

    def fetch_data(self):
        self.logger.info("Fetch data... Current version  > %d ", self.getCurrentVersion())

        infos = {'type': 'LPP', 'version': self.getCurrentVersion(),
                 'date': datetime.datetime.now(datetime.timezone.utc).isoformat(sep='T'),
                 'url': None, 'files': [], 'compl': None}

        test_version = self.getCurrentVersion() + 1
        url_ = 'http://www.codage.ext.cnamts.fr/f_mediam/fo/tips/LPP%d.zip' % test_version

        rcheck = requests.head(url_)
        self.logger.debug("Test version %d code [%d] - %s", test_version, rcheck.status_code, rcheck.text)

        if rcheck.status_code == 200:
            infos["url"] = url_
            infos["version"] = str(test_version)
            compl = self.load_infos(test_version)
            infos["compl"] = self.format_html_compl(compl)

            self.logger.warn(infos)
        else:
            self.logger.warn("Document LPP numero {} non disponible [{}]".format(test_version, rcheck.status_code))

        return infos

    def load_infos(self, version_number):
        """
        Lecture des données dans le fichier de description des versions
        col 1 : N° de VERSION DE LA BASE LPP
        col 2 : Titre et chapitre visés par les textes réglementaires de la version
        col 3 : Dates des arrêtés visés / Avis tarifs & prix
        col 4 : date du JO le plus récent de la version ; elle peut correspondre à un avis tarifs et/ou prix
        col 5 : Date de mise en ligne sur le site Ameli.fr
        col 6 : commentaire

        :param version_number: version concernée
        :return: dictionnaire des informations complémentaires Type: dict
        """
        url_ = 'http://www.codage.ext.cnamts.fr/f_mediam/fo/tips/LPP_TDB%d.xls' % version_number
        act = action.DownloadAction(conf=self.data_conf)
        xlsfile = act.download(url_)

        workbook = xlrd.open_workbook(xlsfile)
        worksheet = workbook.sheet_by_index(0)
        compl = None
        for rownum in range(worksheet.nrows):
            vals = worksheet.row_values(rownum)

            file_version = 0
            try:
                file_version = int(vals[0])
            except ValueError:
                pass

            if file_version == version_number:
                self.logger.info(vals)
                val_1 = '\n'.join(list(filter(lambda x: len(x) > 0, vals[1].split('\n'))))
                val_1 = val_1.replace('&', ' et ')
                val_2 = '\n'.join(list(filter(lambda x: len(x) > 0, vals[2].split('\n'))))
                val_2 = val_2.replace('&', ' et ')
                val_3 = ''
                try:
                    val_3 = datetime.datetime(*xlrd.xldate_as_tuple(vals[3], workbook.datemode)).strftime("%d-%m-%Y")
                except TypeError:
                    self.logger.warn("Erreur conversion info LPP : val 3 = %s" % vals[3])
                    val_3 = vals[3]
                val_4 = ''
                try:
                    val_4 = datetime.datetime(*xlrd.xldate_as_tuple(vals[4], workbook.datemode)).strftime("%d-%m-%Y")
                except TypeError:
                    self.logger.debug("Erreur conversion info LPP : val 4 = %s" % vals[4])
                    val_4 = vals[4]
                val_5 = ''
                if len(vals) > 5:
                    val_5 = vals[5].strip()

                compl = {'version': version_number,
                         'titres_chapitres': val_1,
                         'dates_arretes': val_2,
                         'date_jo': val_3,
                         'date_ameli': val_4,
                         'commentaire': val_5}

        return compl

    @staticmethod
    def format_html_compl(compl):
        with open(os.path.join(WatchDog.CONF_DATA_DIR, 'lpp_compl.html'), 'r') as fin:
            templ = fin.read()
            txt = templ.format(compl['version'], compl['titres_chapitres'],
                               compl['dates_arretes'], compl['date_jo'],
                               compl['date_ameli'])
            return txt


class CCAMWatchDog(WatchDog):
    def fetch_data(self):
        self.logger.info("Fetch data... Current version  > %d ", self.getCurrentVersion())
        baseurl = 'https://www.ameli.fr'
        url2check = '/accueil-de-la-ccam/telechargement/index.php'

        infos = {'type': 'CCAM', 'version': self.getCurrentVersion(),
                 'date': datetime.datetime.now(datetime.timezone.utc).isoformat(sep='T'),
                 'url': None, 'files': [], 'compl': None}

        # ex: CCAM04900_DBF_PART3.zip
        regexdata = re.compile(r'.*?(CCAM(\d+)_DBF_PART(\d+)\.zip)')

        # .../documents/Cam_Note_V46.50.pdf (avec faute sur la CCAM :( )
        # .../documents/Ccam_Note_V47.pdf
        regexcompl = re.compile(r'.*C\w*?m_Note_V(\d+\.?\d*)\.pdf')

        rcheck = requests.get("%s%s" % (baseurl, url2check))

        # parse du contenu
        soup = BeautifulSoup(rcheck.text, "html5lib")

        # sauvegarde
        self.save_srcfile(rcheck.text)

        links = list(filter(lambda x: x.get('href'), soup.find_all('a')))
        pdf_list = list(filter(lambda x: x.get('href').endswith('.pdf'), links))
        zip_list = list(filter(lambda x: x.get('href').endswith('.zip'), links))

        for link in zip_list:
            # recuperation des liens vers les document dbf, complete le dict infos avec les donnees trouvees

            resregex = regexdata.match(link.get('href'))
            if resregex:
                # recuperation du numero de version dans le nom de fichier
                self.logger.debug(resregex.groups())

                v = '{:.02f}'.format(int(resregex.group(2)) / 100)
                if v.endswith('.00'):
                    # version entiere, suppression de .00
                    infos["version"] = v[:-3]
                else:
                    infos["version"] = v
                infos["files"].append('%s%s' % (baseurl, link.get('href')))

        for link in pdf_list:
            # recherche d'un document pdf relatif a la version trouvée des fichiers dbf
            # test si une URL correspondant aux notes de version
            resregcompl = regexcompl.match(link.get('href'))
            if resregcompl:
                self.logger.debug("compl : %s / v=%s" % (resregcompl.groups(), infos["version"]))
                if resregcompl.group(1) == infos["version"]:
                    compl = {'version': infos['version'],
                             'pdf': '{}{}'.format(baseurl, link.get('href'))}
                    infos["compl"] = self.format_html_compl(compl)

        return infos

    @staticmethod
    def format_html_compl(compl):
        with open(os.path.join(WatchDog.CONF_DATA_DIR, 'ccam_compl.html'), 'r') as fin:
            templ = fin.read()
            txt = templ.format(compl['version'], compl['pdf'])
            return txt
