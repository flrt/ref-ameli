#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Analyse des pages sur le site ameli pour détecter les nouvelles versions.

"""
__author__ = 'Frederic Laurent'
__version__ = "1.1"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import datetime
import logging
import os.path
import re

import requests
import xlrd
from bs4 import BeautifulSoup
from easy_atom import action
from easy_atom import atom
from dbfread import DBF

import versions


class WatchDog(versions.VersionDetector):
    CONF_DATA_DIR = 'conf'

    """
    Analyse le changement et enchaine les actions necessaires
    """

    def fetch_data(self):
        raise Exception("DO implement")

    def __init__(self, nomen, feed_conf=None, data_conf=None, mail_conf=None, tweet_conf=None):
        versions.VersionDetector.__init__(self, nomen)
        self.logger = logging.getLogger('%s_wd' % nomen)
        self.nomen = nomen
        self.feed = None
        self.feed_conf = feed_conf
        self.data_conf = data_conf
        self.mail_conf = mail_conf
        self.tweet_conf = tweet_conf

        self.logger.debug("Feed configuration : %s" % self.feed_conf)
        self.logger.debug("Data configuration : %s" % self.data_conf)
        self.logger.debug("Mail configuration : %s" % self.mail_conf)
        self.logger.debug("Twitter configuration : %s" % self.tweet_conf)

        if self.feed_conf:
            self.feed = atom.Feed(self.nomen, selfhref=self.feed_conf['feed_base'])


    def fill_infos(self, **kwargs):
        """
            Construit un dictionnaire d'informations a propos d'une version

        :param kwargs: ensemble de cles/valeurs a positionner dans le dictionnaire
        :return: dictionnaire resultat

        """

        # version de l'information : soit la version passee en parametre ou la version
        # courante
        v = kwargs['version'] if 'version' in kwargs else self.get_current_version()
        _summary = f'Version {v} disponible'
        if kwargs['available'] is False:
            _summary = f'Version {v} en cours de publication'

        # valeurs par defaut
        d = {'type': self.nomen.upper(),
             'id': f'urn:ameli:{self.nomen}:v{v}',
             'version': v,
             'date': datetime.datetime.now(datetime.timezone.utc).isoformat(sep='T'),
             'url': None,
             'title': f'Nomenclature {self.nomen.upper()} Version {v}',
             'summary': _summary,
             'files': [],
             'html': None,
             'available': True}
        # mise a jour avec les donnees en argument
        d.update(kwargs)
        return d

    def summary140(self, infos):
        if infos['available']:
            # Message 140
            # Nomenclature UCD Version 406 disponible #ameli #référentiels (RSS : https://www.opikanoba.org/feeds/ameli_ucd.rss2)
            if self.feed:
                return '{} disponible #ameli #{} #référentiels (Flux RSS : {})'.format(
                    infos['title'], infos['type'], self.feed.feed_url(feed_type='rss2'))
            else:
                return '{} disponible #ameli #{} #référentiels'.format(
                    infos['title'], infos['type'])
        return None


    def process(self):
        """
            Traitement principal
        :return: -
        """

        self.load_previous()

        infos = self.fetch_data()

        # si les infos correspondent a :
        # - une nouvelle version : is_newer
        # - une version qui n'etait pas completement disponible et qui l'est desormais
        if infos and (self.is_newer(infos) or self.in_progress_status_changed(infos)):
            if self.tweet_conf:
                # notification tweeter
                text140 = self.summary140(infos)
                if text140:
                    act = action.TweetAction(conf_filename=self.tweet_conf)
                    url_tweet = act.process(text140)
                    if url_tweet:
                        # 1 seule URL -> recuperation enregistrement 1
                        #{'available': False, 'url_status': [{'url': 'https://www.twitter.com/.../status/...', 'http_status': 301, 'size': '0'}]}
                        url_infos = self.check_urls([url_tweet])['url_status'][0]
                        self.logger.info(url_infos)
                        url_infos['type']='link'
                        infos['files_props'].append(url_infos)

            self.new_version(infos)
            self.save_current_versions()

            if self.feed:
                # https://validator.w3.org/feed/docs/warning/RelativeSelf.html

                feed = self.feed.generate(self.version['versions'])
                self.feed.save(feed)
                self.feed.rss2()

                if self.feed_conf['ftp_config']:
                    act = action.UploadAction(conf_filename=self.feed_conf['ftp_config'])
                    act.process([self.feed.feed_filename, self.feed.rss2_filename])

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
                act = action.SendMailAction(conf_filename=self.mail_conf)
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
            fn = os.path.join(self.data_conf['backup_dir'], "{0}_{1}.html".format(dn, self.nomen.upper()))

            with open(fn, "w") as fout:
                fout.write(content)

    def check_urls(self, urllist=[]):
        """
        Verifie si les fichiers sont bien presents via 1 requete HEAD
        :param urllist: liste des urls
        :return: dict avec 1 status global et les status par URL
        """
        if len(urllist)==0:
            return dict(available=False, url_status=[])

        result=dict(available=True, url_status=[])

        for url in urllist:
            self.logger.debug("Check URL {}".format(url))
            req=requests.head(url)
            _size = 0
            if req.status_code == 200 and 'Content-Length' in req.headers:
                _size = req.headers['Content-Length']

                if int(_size) < 400:
                    req2=requests.get(url)
                    self.logger.debug(req2.text)
                    result['available'] = False

            result['url_status'].append(
                dict(url=url, http_status=req.status_code, size=_size))
            
            result['available'] = result['available'] & (req.status_code==200)
            
        self.logger.debug("CHECKS %s"%result)
        return result

class UCDWatchDog(WatchDog):
    
    def fetch_data(self):
        self.logger.info("Fetch data... Current version  > %d ", self.get_current_version())

        infos = None
        baseurl = 'http://www.codage.ext.cnamts.fr'
        url2check = '/codif/bdm_it/index_tele_ucd.php'

        regexdata = re.compile(
            r'.*?(ucd_total|ucd_maj|ucd_histo_prix|retro_histo_taux|retro_histo_cout_sup)_(\d+)_(\d+)\.dbf')
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

            self.logger.debug(f'DBF Files {len(dbf_list)}')
            [self.logger.debug(f' - {d}') for d in dbf_list]

            dbf_map = {}

            for link in dbf_list:
                # recuperation des liens vers les document dbf

                resregex = regexdata.match(link.get('href'))
                if resregex:
                    # recuperation du numero de version dans le nom de
                    # fichier
                    self.logger.debug(resregex.groups())

                    _version = str(int(resregex.group(2)))
                    if _version not in dbf_map:
                        dbf_map[_version] = []
                    dbf_map[_version].append('%s%s' % (baseurl, link.get('href')))

            if len(dbf_map.keys()) == 1:
                # 1 version = OK
                _version = list(dbf_map.keys())[0]
                # verification de la disponibilite des URL
                url_checked = self.check_urls(dbf_map[_version])
                # ajout du type de donnees
                for u in url_checked['url_status']:
                    u['type']='data' 

                infos = self.fill_infos(version=_version,
                                        files=dbf_map[_version],
                                        files_props=url_checked['url_status'],
                                        available=url_checked['available'],
                                        html=self.format_html_compl(_version, dbf_map[_version]))

            elif len(dbf_map.keys()) > 1:
                self.logger.error("Plusieurs versions  !!! %s" % str(dbf_map.keys()))
            else:
                self.logger.debug("Aucune version trouvee")

        else:
            self.logger.error(
                "Probleme de recuperation du document UCD / ameli [%s]", rcheck.status_code)
            self.logger.error(f"URL : {baseurl} {url2check}")

        return infos

    @staticmethod
    def format_html_compl(version, urls):
        # download
        local_fn = None
        med_regexp = re.compile(r"(\w+).*")
        med_set = set()
        records = []
        txt = ""
        err_txt = ""

        for u in urls:
            if 'ucd_maj' in u:
                da = action.DownloadAction()
                local_fn = da.download(u)

        if local_fn:
            try:
                database = DBF(local_fn, encoding='iso8859-1')
                records = database.records

                for r in records:
                    res_eval = med_regexp.match(r['NOM_COURT'])
                    if res_eval:
                        med_set.add(res_eval.group(1))
            except:
                err_txt = "Erreur de lecture du fichier {}".format(os.path.basename(local_fn))

            with open(os.path.join(WatchDog.CONF_DATA_DIR, 'ucd_compl.html'), 'r') as fin:
                templ = fin.read()
                txt = templ.format(version, len(records), ', '.join(list(med_set)), err_txt)
        return txt



class LPPWatchDog(WatchDog):
    """
    Referentiel LPP

    Données : http://www.codage.ext.cnamts.fr/f_mediam/fo/tips/LPP466.zip
    Infos : http://www.codage.ext.cnamts.fr/f_mediam/fo/tips/LPP_TDB466.xls

    """

    def fetch_data(self):
        self.logger.info("Fetch data... Current version  > %d ", self.get_current_version())

        infos = None
        # VERSION actuelle : PB si nouvelle version pour la mise a jour des donnees dans le DICT
        # A voir infos / versions / maj

        test_version = self.get_current_version() + 1
        url_ = f'http://www.codage.ext.cnamts.fr/f_mediam/fo/tips/LPP{test_version}.zip'

        rcheck = requests.head(url_)
        self.logger.debug("Test version %d code [%d] - %s", test_version, rcheck.status_code, rcheck.text)

        if rcheck.status_code == 200:
            compl = self.load_infos(test_version)

            url_checked = self.check_urls([url_])
            for u in url_checked['url_status']:
                u['type']='data'


            infos = self.fill_infos(version=str(test_version),
                                    files=[url_],
                                    files_props=url_checked['url_status'],
                                    available=url_checked['available'],
                                    html=self.format_html_compl(compl))
        else:
            self.logger.warning("Document LPP numero {} non disponible [{}]".format(test_version, rcheck.status_code))

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
        self.logger.info("Fetch data... Current version  > %d ", self.get_current_version())
        baseurl = 'https://www.ameli.fr'
        url2check = f'{baseurl}/accueil-de-la-ccam/telechargement/index.php'

        # ex: CCAM04900_DBF_PART3.zip
        regexdata = re.compile(r'.*?(CCAM(\d+)_DBF_PART(\d+)\.zip)')

        # .../documents/Cam_Note_V46.50.pdf (avec faute sur la CCAM :( )
        # .../documents/Ccam_Note_V47.pdf
        regexcompl = re.compile(r'.*C\w*?m_Note_V(\d+\.?\d*)\.pdf')

        self.logger.debug(f"Check {url2check}")
        rcheck = requests.get(url2check)

        # parse du contenu
        soup = BeautifulSoup(rcheck.text, "html5lib")

        # sauvegarde
        self.save_srcfile(rcheck.text)

        links = list(filter(lambda x: x.get('href'), soup.find_all('a')))
        pdf_list = list(filter(lambda x: x.get('href').endswith('.pdf'), links))
        zip_list = list(filter(lambda x: x.get('href').endswith('.zip'), links))

        version = None
        files = []
        compl = None

        for link in zip_list:
            # recuperation des liens vers les document dbf

            resregex = regexdata.match(link.get('href'))
            if resregex:
                # recuperation du numero de version dans le nom de fichier
                self.logger.debug(resregex.groups())

                # extraction de la version
                v = '{:.02f}'.format(int(resregex.group(2)) / 100)
                version = v[:-3] if v.endswith('.00') else v
                # ajout des fichiers
                files.append('%s%s' % (baseurl, link.get('href')))
                
        # verification de la disponibilite des URL
        url_checked = self.check_urls(files)
        # ajout du type de donnees
        for u in url_checked['url_status']:
            u['type']='data' 


        for link in pdf_list:
            # recherche d'un document pdf relatif a la version trouvée des fichiers dbf
            # test si une URL correspondant aux notes de version
            href = link.get('href')
            resregcompl = regexcompl.match(href)
            if resregcompl:
                self.logger.debug("compl : %s / v=%s" % (resregcompl.groups(), version))
                if resregcompl.group(1) == version:
                    compl = self.format_html_compl({'version': version,'pdf': f'{baseurl}{href}'})

        return self.fill_infos(
            version=version, 
            files=files, 
            files_props=url_checked['url_status'],
            available=url_checked['available'],
            html=compl)

    @staticmethod
    def format_html_compl(compl):
        with open(os.path.join(WatchDog.CONF_DATA_DIR, 'ccam_compl.html'), 'r') as fin:
            templ = fin.read()
            txt = templ.format(compl['version'], compl['pdf'])
            return txt


class NABMWatchDog(WatchDog):
    """
    Ref NABM
    Page : http://www.codage.ext.cnamts.fr/codif/nabm/index_tele_ucd.php
    """

    def fetch_data(self):
        self.logger.info("Fetch data... Current version  > %d ", self.get_current_version())
        
        files = []
        test_version = self.get_current_version() + 1
        url_base = "http://www.codage.ext.cnamts.fr/codif/nabm/download_file.php?filename=/f_mediam/fo/nabm/"
        nabm_files = ["NABM_FICHE_TOT%03d.dbf" % test_version,
                      "NABM_HISTO_TOT%03d.dbf" % test_version,
                      "NABM_INCOMP_TOT%03d.dbf" % test_version]

        urltest = "{}{}".format(url_base, nabm_files[0])
        self.logger.debug(f"Test URL {urltest}")

        rcheck = requests.head(urltest)
        self.logger.debug("Test version %d code [%d] - %s", test_version, rcheck.status_code, rcheck.text)

        if rcheck.status_code == 200:
            files = list(map(lambda x: "{}{}".format(url_base, x), nabm_files))
                # verification de la disponibilite des URL
            url_checked = self.check_urls(files)
            # ajout du type de donnees
            for u in url_checked['url_status']:
                u['type']='data' 

            return self.fill_infos(
                version=str(test_version), 
                files=files, 
                files_props=url_checked['url_status'],
                available=url_checked['available'])
        else:
            self.logger.warning("Documents NABM numero {} non disponible [{}]".format(test_version, rcheck.status_code))
            return None
      

