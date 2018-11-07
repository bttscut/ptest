#coding=utf8
from pysproto import SprotoRpc
from pysproto import sprotoparser as sparser
import codecs
import os

sproto_obj = None
sproto_desc = {"type": {}, "protocol": {}}
sproto_file_desc = {}


def init_parser(sprotos_path, need_file_desc=False):
    global sproto_desc
    global sproto_file_desc

    try:
        sproto_list = []
        for root, dirs, files in os.walk(sprotos_path):
            for filepath in files:
                if filepath[0] == "." or filepath[1] == "_" or not filepath.endswith(
                        ".sproto"):
                    continue
                abs_path = os.path.abspath(os.path.join(root, filepath))
                sproto_text = codecs.open(abs_path, encoding="utf-8").read()
                sproto_list.append((sproto_text, filepath))
        sproto_desc = sparser.parse_list(sproto_list)
        if need_file_desc:
            for root, dirs, files in os.walk(sprotos_path):
                for filepath in files:
                    if filepath[0] == "." or filepath[1] == "_" or not filepath.endswith(
                            ".sproto"):
                        continue
                    abs_path = os.path.abspath(os.path.join(root, filepath))
                    name = os.path.splitext(filepath)[0]
                    text = codecs.open(abs_path, encoding="utf-8").read()
                    sproto_file_desc[name] = sparser.parse(text, name, False)

        return True
    except Exception, e:
        print('Failed: %s' % e)
        return False


def init_sproto_obj(spb_path, base_package):
    print('init sproto obj', spb_path, base_package),
    global sproto_obj
    try:
        with open(spb_path, "rb") as f:
            pbin = f.read()
        sproto_obj = SprotoRpc(pbin, base_package)
        return True
    except Exception, e:
        print('Failed: %s' % e)
        return False


def init_proto(sprotos_path, spb_path, base_package, parse=True):
    if parse:
        if not init_parser(sprotos_path, need_file_desc=parse):
            return False
    if not init_sproto_obj(spb_path, base_package):
        return False
    return True
