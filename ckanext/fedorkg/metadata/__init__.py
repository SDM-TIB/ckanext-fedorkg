import os

from DeTrusty.Molecule.MTManager import SPARQLConfig

STORAGE_PATH = os.environ.get('CKAN_STORAGE_PATH', '/var/lib/ckan')
FEDORKG_PATH = os.path.join(STORAGE_PATH, 'fedorkg')
SEMSD_PATH = os.path.join(FEDORKG_PATH, 'rdfmts.ttl')


class MetadataConfig:
    instance = None

    def __new__(cls):
        if not MetadataConfig.instance:
            os.makedirs(FEDORKG_PATH, exist_ok=True)
            MetadataConfig.instance = SPARQLConfig('http://localhost:9000/sparql')
        return MetadataConfig.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)
