# Mirador python client
# @author nickjacob (nick@mirador.im)
from client import MiradorClient
from errors import MiradorException
from os import getenv as _genv

import client
import ext


def classify_files(files, api_key=None):
    "procedural: classify files given the `api_key`"
    api_key = api_key or _genv('MIRADOR_API_KEY')

    if not api_key:
        raise MiradorException('no api key provided')
    return MiradorClient(api_key).classify_files(*files)


def classify_urls(urls, api_key=None):
    "procedural: classify urls given the `api_key`"
    api_key = api_key or _genv('MIRADOR_API_KEY')

    if not api_key:
        raise MiradorException('no api key provided')
    return MiradorClient(api_key).classify_urls(*urls)
