from fastcore.imports import *
from fastcore.foundation import *
from fastcore.utils import *
from fastcore.test import *

import os,re,json,glob,collections,pickle,shutil,inspect,yaml,tempfile,enum,stat,time,random,sys
import importlib.util
from functools import lru_cache
from pdb import set_trace
from configparser import ConfigParser
from pathlib import Path
from textwrap import TextWrapper
from typing import Union,Optional
from functools import partial,lru_cache
from base64 import b64decode,b64encode

_defaults = {"host": "github", "doc_host": "https://%(user)s.github.io", "doc_baseurl": "/%(lib_name)s/"}

def _add_new_defaults(cfg, file, **kwargs):
    for k,v in kwargs.items():
        if cfg.get(k, None) is None:
            cfg[k] = v
            save_config_file(file, cfg)

@lru_cache(maxsize=None)
def get_config(cfg_name='settings.ini'):
    cfg_path = Path.cwd()
    while cfg_path != cfg_path.parent and not (cfg_path/cfg_name).exists(): cfg_path = cfg_path.parent
    config = Config(cfg_path, cfg_name=cfg_name)
    _add_new_defaults(config.d, config.config_file,
            host="github", doc_host="https://%(user)s.github.io", doc_baseurl="/%(lib_name)s/")
    return config


def create_config(host, lib_name, user, path='.', cfg_name='settings.ini', branch='master',
               git_url="https://github.com/%(user)s/%(lib_name)s/tree/%(branch)s/", custom_sidebar=False,
               nbs_path='nbs', lib_path='%(lib_name)s', doc_path='docs', recursive=False, tst_flags='', version='0.0.1',
               doc_host="https://%(user)s.github.io", doc_baseurl="/%(lib_name)s/", **kwargs):
    "Creates a new config file for `lib_name` and `user` and saves it."
    g = locals()
    config = {o:g[o] for o in 'host lib_name user branch git_url lib_path nbs_path doc_path recursive tst_flags version custom_sidebar'.split()}
    config = {**config, **kwargs}
    save_config_file(Path(path)/cfg_name, config)

#export
class ReLibName():
    "Regex expression that's compiled at first use but not before since it needs `get_config().lib_name`"
    def __init__(self, pat, flags=0): self._re,self.pat,self.flags = None,pat,flags
    @property
    def re(self):
        if not hasattr(get_config(), 'lib_name'): raise Exception("Please fill in the library name in settings.ini.")
        self.pat = self.pat.replace('LIB_NAME', get_config().lib_name)
        if self._re is None: self._re = re.compile(self.pat, self.flags)
        return self._re

def parse_line(line):
    "Convert list-like string into a list"
    line = line.strip()
    if line.startswith('[') and line.endswith(']'): line=line[1:-1]
    return [s for s in re.split('[ ,]+', line) if s]

