import os
from http import HTTPStatus

import requests
from DeTrusty.Molecule.MTManager import SPARQLConfig

STORAGE_PATH = os.environ.get('CKAN_STORAGE_PATH', '/var/lib/ckan')
FEDORKG_PATH = os.path.join(STORAGE_PATH, 'fedorkg')
SEMSD_PATH = os.path.join(FEDORKG_PATH, 'rdfmts.ttl')

os.makedirs(FEDORKG_PATH, exist_ok=True)


class MetadataConfig:
    instance = None

    class __MetadataConfig(SPARQLConfig):
        def __init__(self, url):
            super().__init__(url)

        def saveToFile(self, path):
            headers = {'Accept': '*/*', 'Content-type': 'application/text'}
            resp = requests.post('http://localhost:9000/serialize',
                                 headers=headers,
                                 params={'path': path})
            if resp.status_code == HTTPStatus.OK:
                return True
            else:
                raise Exception(resp.json()['error'])

    def __new__(cls):
        if not MetadataConfig.instance:
            MetadataConfig.instance = MetadataConfig.__MetadataConfig('http://localhost:9000/sparql')
            MetadataConfig.instance.set_update_credentials('http://localhost:9000/sparql-update', '', '')
        return MetadataConfig.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)
