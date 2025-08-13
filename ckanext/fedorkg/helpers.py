
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit


def is_fedorkg_page():
    # exclude the admin and dashboard page
    return False if 'ckan-admin' in h.current_url() else '/fedorkg' in h.current_url()


def icon():
    if toolkit.check_ckan_version(min_version='2.10'):
        return 'magnifying-glass'
    else:
        return 'search'
