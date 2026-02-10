import ckan.plugins.toolkit as toolkit


def fedorkg_admin(context, data_dict):
    return {'success': toolkit.check_access('sysadmin', context)}
