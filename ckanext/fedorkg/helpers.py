
import ckan.lib.helpers as h


def is_fedorkg_page():
    return '/fedorkg' in h.current_url()
