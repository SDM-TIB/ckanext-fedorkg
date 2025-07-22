import os

STORAGE_PATH = os.environ.get('CKAN_STORAGE_PATH', '/var/lib/ckan')
FEDORKG_PATH = os.path.join(STORAGE_PATH, 'fedorkg')
SEMSD_PATH = os.path.join(FEDORKG_PATH, 'rdfmts.ttl')
