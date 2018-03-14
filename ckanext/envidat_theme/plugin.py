import ckan.plugins as plugins
from ckan.lib.plugins import DefaultTranslation

import ckan.plugins.toolkit as toolkit

from ckanext.envidat_theme import helpers

class Envidat_ThemePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IValidators)
    
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'envidat_theme')

    # ITemplateHelpers
    def get_helpers(self):
        return {'envidat_theme_get_children_packages': helpers.envidat_theme_get_children_packages,
                 'envidat_theme_get_citation': helpers.envidat_theme_get_citation,
                 'envidat_theme_get_datamanager_choices': helpers.envidat_theme_get_datamanager_choices,
                 'envidat_theme_get_datamanager_user': helpers.envidat_theme_get_datamanager_user,
                 'envidat_theme_set_default': helpers.envidat_theme_set_default,
                 'envidat_theme_get_markup': helpers.envidat_theme_get_markup }

    # IValidators
    def get_validators(self):
        return { 'envidat_string_uppercase': validation.envidat_string_uppercase }
