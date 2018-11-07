# -*- coding: utf-8 -*-
import ConfigParser
import sys

parser = ConfigParser.SafeConfigParser()
default_cfg_file = 'config.ini'
cfg_file = None

def read(filename):
    global cfg_file
    cfg_file = filename
    parser.read(filename)

def get(section, key, default=None):
    try:
        return parser.get(section, key)
    except:
        return default
