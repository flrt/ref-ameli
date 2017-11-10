#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Fonctions d'aide pour le logging, la lecture de configuration

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import json
import logging
import os.path
import sys


def load_json_config(config_filename):
    """
    Lecture d'un fichier de configuration au format JSON
    Produit un dictionnaire python

    :param config_filename: nom du fichier
    :return: données lues dans 1 dictionnaire
    """
    if not os.path.exists(config_filename):
        return {}
    else:
        with open(config_filename, 'r') as fin:
            try:
                return json.loads(fin.read())
            except TypeError:
                return {}


def make_error_logger(name, level, filename):
    """
        Création d'un Logger d'erreur

    :param name: nom du logger
    :param level: niveau de logging
    :param filename: nom du fichier d'erreur
    :return: logger
    """
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",
                                  "%d/%m %H:%M:%S")
    sth_err = logging.FileHandler(filename)
    sth_err.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(sth_err)
    logger.setLevel(level)
    return logger


def config_logger(streamhandler, name, level, fmt=None):
    """
    Configure un logger sur la sortie standard avec un niveau
    :param fmt: formatter
    :param streamhandler: handler
    :param name: nom du logger
    :param level: niveau
    :return: logger ou loggers
    """
    if not fmt:
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s")
    else:
        formatter = logging.Formatter(fmt)
    streamhandler.setFormatter(formatter)

    # if there are multiple logger to set
    if isinstance(name, list):
        loggers = []
        for logname in name:
            # print "Logger [%s] addHandler %s - level %s" % (logname, streamhandler, level)

            logger = logging.getLogger(logname)
            logger.addHandler(streamhandler)
            logger.setLevel(level)
            loggers.append(logger)
        return loggers
    else:
        # print "Logger [%s] addHandler %s" % (name, sth_sysout)
        logger = logging.getLogger(name)
        logger.addHandler(streamhandler)
        logger.setLevel(level)
        return logger


def stdout_logger(name, level):
    """
        Création d'un logger sur la sortie standard
    :param name: nom du logger
    :param level: niveau
    :return: logger
    """
    sth_sysout = logging.StreamHandler(sys.stdout)
    return config_logger(sth_sysout, name, level)


def file_logger(filename, name, level):
    """
        Création d'un logger dans 1 fichier
    :param filename: nom du fichier
    :param name: nom du logger
    :param level: niveau
    :return: logger
    """
    sth_file = logging.FileHandler(os.path.abspath(filename))
    return config_logger(sth_file, name, level)
